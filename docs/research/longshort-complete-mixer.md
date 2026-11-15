# Testing so far: complete-mixer quantum proposal on a 6 long / 6 short ETF book

This note covers one line of work: a quantum circuit that proposes moves for a Markov
chain search, applied to the question **which 6 of 12 ETFs should we hold long and which
6 short** so the book has the lowest risk. It covers the problem, the circuit, every
test run so far, and where the result stands. Code and raw numbers are in
`experiments/longshort/` and `results/longshort_*`. The running log is
`experiments/longshort/README.md` (beads b3d and kaa).

## 1. The portfolio problem

**Universe.** The first 12 ETFs of the project basket:

| Equity | Bonds | Real assets / other |
|---|---|---|
| SPY, IWM, EFA, EEM, VNQ | IEF, TLT, TIP, LQD, HYG | GLD, DBC |

A second universe of 16 large US stocks (2 per sector, 2010 membership) is used as a
check that results are not specific to ETFs.

**Data.** Daily adjusted closes, 2009–2025. There are 64 quarterly windows (2010Q1–2025Q4),
and each uses the previous 252 trading days to estimate the covariance matrix Σ.

**Book.** Every ETF is held at equal size: s_i = +1 (long) or −1 (short), exactly 6 of
each. The score is the negative variance of the book:

    S(s) = − sᵀ Σ s / n²        (risk only, no expected-return term)

The search maximises S, which minimises risk. ETFs that move together want to sit on
opposite sides, so a long SPY offsets a short IWM. Not every correlated pair can be split
this way at once (frustration). With one dominant market factor the problem is close to
balanced number partitioning of the betas, a classic hard landscape.

**Encoding.** Flipping every sign gives the same risk, so ETF 0 (SPY) is fixed long. The
state is which 5 of the other 11 ETFs are also long. That is an 11-bit string with exactly
five 1s, giving C(11,5) = 462 valid books. One **swap** moves one long to short and one
short to long. The count-preserving tools from the long-only work (`StateSpace`, swap
neighbours, XY circuits) apply unchanged.

## 2. Why this problem: the landscape is rugged

Earlier long-only problems (pick k of n, maximise return minus risk) turned out to have a
single swap optimum in every window. On those, greedy descent always wins and no proposal
can help. The long/short book is the first real-data problem in the project that is hard
for greedy search (`python -m qemcmc.longshort`, `results/longshort_landscape.csv`):

| Universe | Book | Windows with > 1 local optimum | Median optima | Max | Greedy success (median / min) |
|---|---|---|---|---|---|
| ETFs | 6 / 6 | 100% | 5.5 | 10 | 0.33 / 0.11 |
| ETFs | 8 / 8 | 100% | 13 | 31 | 0.21 / 0.07 |
| Stocks | 6 / 6 | 94% | 2.5 | 6 | 0.55 / 0.21 |
| Stocks | 8 / 8 | 100% | 6 | 12 | 0.36 / 0.13 |

"Greedy success" is the fraction of random starts from which steepest-descent swaps reach
the global best book. On the 6 / 6 ETF book a typical greedy run succeeds only one time
in three.

## 3. The quantum proposal

Each Metropolis step runs one circuit on the 11 free qubits, starting from the current
book |s⟩, and measures a proposed book s′:

    U = A(β)ᵀ · P(γ) · A(β)        (mix, score phase, mirrored mix)

- **Mixer A(β).** XY (`XXPlusYYGate`) rotations between pairs of qubits. They swap a long
  and a short and never change the count, so every measurement is a valid 6 / 6 book.
- **Complete mixer.** XY gates between **all 55 pairs** of the 11 qubits, so any long can
  trade with any short in one layer. The earlier **ring** mixer only couples neighbours
  in ticker order. The **ordered ring** puts the most strongly coupled ETFs next to each
  other.
- **Score phase P(γ).** e^{iγ·S(x)} using the book's per-asset terms h and all pair terms J
  (the "full" phase), with γ = g / std(S).
- **Palindromic form.** The circuit is mirrored, so the proposal is symmetric
  (Q[s→s′] = Q[s′→s]). The plain Metropolis accept rule is therefore exact, and the chain
  samples π ∝ exp(S/T) correctly.

All tests simulate the circuit exactly within the 462-state subspace
(`qemcmc/subspace.py`), building the full proposal table Q once per window. Chains are then
table lookups, and spectral gaps are exact eigenvalue computations. No shots and no noise
yet.

## 4. Classical baselines

| Method | Proposal | Score evaluations per attempt |
|---|---|---|
| Single swap | one random long ↔ short swap (local Kawasaki) | 1 |
| Multi-swap | pick j ≤ m uniformly, then a random book j swaps away (global Kawasaki); m tuned | 1 |
| Locally balanced | informed swap weighted by √(score gain), MH-corrected | k(n−k) = 30 |
| Parallel tempering | 4 replicas, T to 10T, swap moves | 1 per replica |

## 5. Tests and results

The temperature is T = 0.1 × std(S) throughout. The mixing metric is the exact spectral
gap of the Metropolis chain divided by the single-swap gap (> 1 means faster mixing).

### Test 1: Ring mixer vs classical (first pilot)

Best (β, g) per window. The ring-mixer quantum proposal beat single swap in 92% of ETF
windows (median 1.56×), but it **never** beat tuned multi-swap (2.34×) on ETFs.

### Test 2: Does the mixer layout explain the loss? (`mixer_test.py`)

All 64 windows, full score phase, β ∈ {0.1, 0.2, 0.3, 0.5, 0.75, 1.0}, g ∈ {1, 3}.
Median gap vs single swap:

| Universe | Tuned multi-swap | Locally balanced | Ring | **Complete** | Ordered ring | Complete beats multi-swap |
|---|---|---|---|---|---|---|
| ETFs | 2.34 | 3.35 | 1.77 | **2.68** | 2.22 | **89%** of windows |
| Stocks | 1.32 | 6.36 | 1.35 | **2.08** | 1.89 | **88%** |

The complete mixer was the first quantum proposal in the project to beat a tuned
long-jump classical baseline on real data. Its best β was usually 0.3.

### Test 3: Is it the score phase or just longer jumps? (`phase_control.py`)

Same complete-mixer circuit with the phase turned off:

| Universe | Phase off | Phase on | Phase on helps | Beats multi-swap (phase off) |
|---|---|---|---|---|
| ETFs | 1.84 | 2.68 | 100% of windows (median 1.46×) | 0% |
| Stocks | 1.05 | 2.08 | 98% (median 1.90×) | 17% |

The gain comes from the **score information** in the circuit. On ETFs the complete mixer's
mean jump (2.6 swaps) is actually shorter than multi-swap's (3.0).

### Test 4: Fair tuning (`fair_tuning.py`)

The quantum side was tuned over 12 settings per window, multi-swap over 4. To remove that
advantage, each method's single setting was chosen on the 32 even windows and then tested
**fixed** on the 32 odd windows:

| Method (fixed setting) | ETFs | Beats multi-swap | Stocks | Beats multi-swap |
|---|---|---|---|---|
| Complete + full phase (β 0.3, g 3) | **2.67** | **81%** | **1.93** | **91%** |
| Multi-swap (m = 5 ETFs / 4 stocks) | 2.22 | — | 1.21 | — |
| Locally balanced | 3.42 | 91% | 6.01 | 97% |
| Ordered ring + ring phase | 1.80 | 22% | 0.93 | 16% |
| Ring + linear phase | 1.42 | 3% | 0.55 | 3% |

The mixing advantage survives held-out testing.

### Test 5: Hardware cost (`compile_depth.py`, `results/longshort_compile_depth.txt`)

Transpiled at optimisation level 3 to IBM fake backends:

| Circuit (11 qubits, 6 / 6) | 2q gates FakeFez | 2q gates FakeTorino | 2q depth |
|---|---|---|---|
| Ring + linear phase | 83 | 56 | 56–63 |
| Ordered ring + ring phase | 87 | 87 | 78–81 |
| Ring + full phase | 241 | 237 | 127–138 |
| **Complete + full phase** | **541** | **569** | **234–272** |

At 8 / 8 (15 qubits) the complete circuit needs about 1,100 two-qubit gates. The winning
circuit is far too deep for current heavy-hex hardware, and the cheap circuits lose the
advantage (Test 4).

### Test 6: Race to the best book (`race.py`)

Mixing fast is not the same as finding the optimum fast. Each method used its fixed
setting from Test 4 and started from matched random books. We counted attempts until the
chain first reached the global best book S* (budget 3,000 attempts at 6 / 6, 15,000 at
8 / 8; at least 99% of runs solved).

| Median attempts (score evals) | ETFs 6 / 6 | Stocks 6 / 6 | ETFs 8 / 8 | Stocks 8 / 8 |
|---|---|---|---|---|
| Locally balanced | 38 (1,140) | 12 (360) | 162 (9,072) | 66 (3,668) |
| **Single swap** | **179** | **100** | **1,093** | **452** |
| Quantum, complete + full | 184 | 125 | 1,264 | 890 |
| Parallel tempering | 199 | 139 | 1,405 | 887 |
| Multi-swap | 215 | 188 | 2,175 | 1,214 |

6 / 6: 32 test windows × 40 starts. 8 / 8: 8 test windows × 24 starts.

## 6. Where we stand

**What holds up**

1. The 6 long / 6 short ETF book is a genuinely rugged real-data problem: several local
   optima in every window, and greedy search succeeds about a third of the time.
2. The complete-mixer quantum proposal **mixes faster** than the strongest blind classical
   proposal (tuned multi-swap): 2.67× vs 2.22× single swap on held-out ETF windows, better
   in 81% of them.
3. The edge comes from the score phase, not from longer jumps.

**What does not**

1. **Finding the optimum.** Plain single-swap Metropolis reaches the best book in the
   fewest attempts of all one-evaluation methods. The quantum proposal is about even on
   ETFs at 6 / 6 (184 vs 179) and 1.2–2× slower elsewhere.
2. **Informed classical search.** Locally balanced swaps beat everything per attempt, but
   each attempt costs 30 score evaluations. Per score evaluation they fall to about
   0.11× / 0.21× single swap.
3. **Hardware.** The complete mixer needs about 550 two-qubit gates at 11 qubits. The
   hardware-friendly ring circuits lose the advantage.

**Current claim (narrowed):** on the rugged long/short ETF book, a score-aware
complete-mixer circuit gives a better-mixing sampler than tuned global swaps, but it does
not yet find the minimum-risk long/short split faster than simple swap search.

**Caveats.** Exact noiseless simulation only. One fixed temperature. Settings were tuned
for mixing, not for hitting the optimum. No shot or wall-clock costs. 8 / 8 was tested on
only 2 windows (gaps) and 8 windows (race).

## 7. Open next steps

- Re-tune β, g and T for hitting time rather than spectral gap, then rerun the race.
- Repeat the 8 / 8 gap test on all 64 windows.
- Look for a shallower mixer that keeps the phase-driven gain: a few complete layers on
  the strongest J pairs only, or ordered ring with the full phase.
- Add shot noise: sample Q from a finite number of shots, and later from FakeFez with noise.
- Cost per shot and per second alongside attempts and score evaluations (project
  convention: log them as separate fields).

## Reproduce

```bash
python -m qemcmc.longshort                          # landscape + gaps at 6 / 6
python -m qemcmc.longshort --big                    # gaps at 8 / 8 (2 windows)
PYTHONPATH=. python experiments/longshort/mixer_test.py
PYTHONPATH=. python experiments/longshort/phase_control.py
PYTHONPATH=. python experiments/longshort/fair_tuning.py
PYTHONPATH=. python experiments/longshort/compile_depth.py
PYTHONPATH=. python experiments/longshort/race.py
```
