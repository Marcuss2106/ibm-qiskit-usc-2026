# Research results: QeMCMC on the market-neutral long–short book

Self-contained context for an agent or teammate picking up this project. It covers the
winning idea, how we got there, the exact formulation, every key number, what the
result does and does not support, how to reproduce it, and what is left.

- Date of results: 2026-11-14/15. All work is on branch `pilot/factor-selection`, which
  GitHub `main` tracks (fast-forwarded), including the hardware commit `ab759a7`.
- Task tracking: beads (`bd show <id>`). Project guide: `docs/DEVELOPMENT.md`. Literature:
  `docs/research/references.md`, `docs/research/rugged-landscapes.md`.
- Conventions: all scores are maximised; "gap ratio" means a method's spectral gap
  divided by single-swap Metropolis's gap on the same instance and temperature (above
  1 = mixes faster); medians are over windows unless stated.

---

## 1. One-paragraph summary

The project asks whether a count-preserving quantum circuit (XY mixer plus a score
phase) makes a better MCMC proposal than classical swap moves on a real financial
selection problem with an exact answer key. On the original problem (equal-weight
mean–variance: choose k of n ETFs) and three other real-data problems, the landscape is
almost always single-peaked, so classical swaps win. The **winning idea** is a
**market-neutral long–short book**: hold all n assets at equal size, half long and half
short, and choose the split that minimises risk. On real ETF and stock data this
landscape is genuinely rugged (median 13 local optima at 8 long / 8 short on ETFs). On
it, a quantum proposal with a **complete XY mixer and the full score phase** **mixes
faster** (exact spectral gap) than single-swap and tuned multi-swap Metropolis in
81–91% of held-out windows, and a phase-off control shows the gain comes from the score
phase. It is a **sampling** result: it does **not** find the single best book faster
(plain single-swap Metropolis does), it is **simulation only** (the circuit needs about
540 two-qubit gates), and on IBM hardware the hardware-cheap version mixes slower than
single swap.

---

## 2. How we got here (why this problem)

### 2.1 The original problem was too easy

Original objective (`docs/DEVELOPMENT.md` §3): choose exactly k of n ETFs, equal weight,
maximise mean–variance. With x a 0/1 vector with k ones, the score is:

$$
S(x) = \frac{1}{k}\,\mu^\top x \;-\; \frac{\lambda}{k^2}\, x^\top \Sigma x
$$

Landscape check (`qemcmc/landscape.py`, 64 quarterly 252-day windows 2010Q1–2025Q4,
20 ETFs): at 5 of 16 with λ = 1, 3, 10, **all 64 windows have exactly one local optimum
under single swaps**, and steepest ascent reaches the optimum from every start. Exact
spectral gaps (`qemcmc/gaps.py`): the quantum proposal mixes at **0.48–0.80×** single
swap at 5 of 16 (never above 1 in any window).

### 2.2 Why: the market factor

Controls in `experiments/landscape/` (see its README) separated data from method:

| Test (5 of 16) | Result |
|---|---|
| μ shrinkage, 63/126/252-day windows | Still single-peaked (max 3 optima) |
| 16 large stocks instead of ETFs | Still single-peaked (max 5) |
| Real volatilities, **random** correlations, risk-only | Median **12** optima, greedy success 0.19 |
| Random correlations plus a growing common market factor | Median optima 12 → 8 → 2 → 1 |
| Real Σ minus its top principal component, risk-only | 84% of windows rugged, median 3 |
| Same, but with returns kept (λ = 3) | Single-peaked again |
| M♮ (valuated-matroid) exchange condition | Violated ~23% for real and random data alike: theory does not explain it |

Mechanism: one common factor makes most pairs positively correlated (substitutes), and
node (single-asset) terms are about 13× larger than edge (pair) terms at λ = 3. A
single-peaked swap landscape follows. Literature agrees that the largest eigenvalue of
asset correlations is a market mode (Plerou et al. 2002), and Stopfer et al. (2025) find
real portfolio instances solved exactly by MIP in seconds.

### 2.3 Other real-data problems we tried (all single-peaked)

| Problem | Where | Rugged? | Quantum vs single swap (gap) |
|---|---|---|---|
| Equal-weight mean–variance, ETFs | `qemcmc/gaps.py` | No | 0.48–0.80× |
| Bayesian factor selection for SPY returns (g-prior posterior) | `experiments/factor_pilot/` | No (>1 optimum in 3–11% of windows) | 0.12–0.25× |
| Multi-factor hedge book (16 instruments, 5 risk factors, risk on correlations) | `experiments/hedgebook/` | No (>1 optimum in 18%, max 3) | 0.43× |
| Difficulty dial: real Σ with market removed, then random correlations | `experiments/dial/` | Only at the random, risk-only end | 1.10× there (multi-swap 1.19×) |

Key lesson from the hedge book: strong hedges are not enough. Real hedges come in
**independent pairs** (equity with volatility, dollar with euro), so their benefits add
and one book wins. Ruggedness needs **frustration**: hedges that conflict, where
completing one breaks another.

### 2.4 Why the long–short book works

In a long–short book, positively correlated assets want to be on **opposite sides**. For
three mutually correlated assets that is impossible for every pair, so the market factor
creates frustration everywhere instead of making the landscape smooth. Under a one-factor
model the risk is approximately:

$$
\text{risk} \approx \sigma_m^2\Big(\sum_{\text{long}}\beta_i - \sum_{\text{short}}\beta_i\Big)^2 + \text{idiosyncratic terms}
$$

so minimising it is close to **balanced number partitioning** of the betas, a classic
rugged problem; long/short portfolios were mapped to spin glasses by Galluccio, Bouchaud
& Potters (1998). It also fits the circuit unchanged: "exactly n/2 longs" is a fixed
count, so the count-preserving XY mixer applies directly.

---

## 3. The winning formulation (exact)

### 3.1 Problem

- Hold all n assets at equal weight 1/n; s_i = +1 long, −1 short; exactly n/2 long.
- Score (maximised) is minus the book's variance, using the real annualised covariance
  Σ of the window (risk-only; no returns):

$$
S(s) = -\frac{1}{n^2}\, s^\top \Sigma\, s
$$

- **Mirror symmetry**: s and −s have the same risk, so every book has a twin. Broken by
  fixing **asset 0 long**. The state is which n/2 − 1 of the other n − 1 assets are long:
  a bit string x of length n − 1 with exactly n/2 − 1 ones (bit = 1 means long). One swap
  = move one long to short and one short to long.
- Sizes: "6 long / 6 short" = n = 12, 11 qubits, C(11, 5) = 462 books; "8 long / 8 short"
  = n = 16, 15 qubits, C(15, 7) = 6,435 books; hardware "4 / 4" = n = 8, 7 qubits,
  C(7, 3) = 35 books.
- Code: `qemcmc/longshort.py` (`book_signs`, `longshort_scores`, `longshort_terms`).

### 3.2 Node and edge weights (for the circuit phase)

Write a = Σ[0, 1:] (covariances with the fixed asset) and B = Σ[1:, 1:]. Up to a constant,
S = Σ_i h_i x_i + Σ_{i<j} J_ij x_i x_j with:

$$
h_i = -\frac{4a_i - 4\sum_j B_{ij} + 4B_{ii}}{n^2}, \qquad J_{ij} = -\frac{8\,B_{ij}}{n^2}
$$

Positive covariance gives negative J (the pair is penalised for sitting on the same
side). Tested: phase scores reproduce S exactly up to a constant
(`tests/test_longshort.py`).

### 3.3 Data

- ETFs: the 20-ETF basket in `qemcmc/data.py` (core SPY IWM EFA EEM IEF TLT GLD DBC, then
  VNQ TIP LQD HYG, XLE XLK XLV EWJ, XLF XLU AGG SLV); n = 12 or 16 uses the first n.
- Stocks (2 largest per sector as of 2010): AAPL MSFT XOM CVX JPM WFC JNJ PFE WMT PG GE
  UPS T VZ MCD AMZN. Cached in `data/stock_prices.csv` (git-ignored; re-downloaded by
  `stock_windows()` if missing).
- Windows: 64 quarter ends 2010Q1–2025Q4, last 252 simple daily returns, Σ annualised ×252.

---

## 4. The quantum proposal

### 4.1 Circuit

Palindromic, one cost layer between two mixer blocks (`qemcmc/circuits.py`):

$$
U = M(\beta)^{\text{rev}}\; P(\gamma)\; M(\beta)
$$

- M(β): one pass of `XXPlusYYGate(2β, 0)` on each mixer edge. **Ring**: ring edges in a
  given order; **complete**: every pair (55 gates at 11 qubits).
- P(γ): exp(iγ·S_phase(x)) via RZ (node terms) and RZZ (edge terms). Phase variants:
  `none`, `linear` (nodes only), `ring` (nodes + ring-adjacent edges), `full` (all edges).
- M^rev: same gates, reverse order. All gates are complex-symmetric, so U = Uᵀ and the
  proposal table Q[s, s'] = |⟨s'|U|s⟩|² is symmetric; plain Metropolis acceptance is
  exact. Tested (`tests/test_circuits.py`), including that a non-palindromic version is
  NOT symmetric.
- Scaling: γ = g / std(S) over valid books. Qubit i = asset i+1; measurement keys map to
  books with `StateSpace.rank_of_int(int(key, 2))`.

### 4.2 Intuition

The mixer spreads the current book into a superposition of nearby trades; the cost layer
stamps each candidate with a phase set by its score; the reversed mixer recombines them so
paths interfere, and books whose phases line up become likely. With the phase off the
reverse block would undo the forward block exactly.

### 4.3 Simulation

`qemcmc/subspace.py` simulates only the C(n−1, n/2−1) valid books: U = Aᵀ·diag(p)·A, with A
the mixer block restricted to valid books (built once per β). About 1 s per table at
4,368 states vs ~350 s by full statevector; tested equal to Qiskit statevector tables to
1e-10 (`tests/test_subspace.py`).

### 4.4 Why the complete mixer

The ring mixer only lets ring-adjacent assets trade directly. With it, the quantum
proposal beat single swap but lost to multi-swap: it was jumping *farther*, not
*smarter*. The complete mixer lets any pair trade; with it the gain over multi-swap
appears, and the phase-off control (5.3) shows it comes from the score information.

---

## 5. Results

### 5.1 Landscape (64 windows; `results/longshort_landscape.csv`)

| Universe | Book | Windows > 1 optimum | Windows > 5 | Median optima | Max | Greedy success (median / min) |
|---|---|---|---|---|---|---|
| ETFs | 6 / 6 | 100% | 50% | 5.5 | 10 | 0.33 / 0.11 |
| ETFs | 8 / 8 | 100% | 100% | 13 | 31 | 0.21 / 0.07 |
| Stocks | 6 / 6 | 94% | 2% | 2.5 | 6 | 0.55 / 0.21 |
| Stocks | 8 / 8 | 100% | 61% | 6 | 12 | 0.36 / 0.13 |

### 5.2 Mixing (exact spectral gaps), main result

Fair tuning (`experiments/longshort/fair_tuning.py`, `results/longshort_fair_tuning_n12.csv`):
6 long / 6 short; each method gets **one** setting chosen on the 32 even windows and is
tested **fixed** on the 32 odd windows. T = 0.1 × std(S).

| Method | ETFs setting | ETFs median | Beats multi-swap | Stocks setting | Stocks median | Beats multi-swap |
|---|---|---|---|---|---|---|
| **Quantum, complete mixer + full phase** | β 0.3, g 3 | **2.67** | **81%** | β 0.3, g 3 | **1.93** | **91%** |
| Locally balanced informed swaps | — | 3.42 | 91% | — | 6.01 | 97% |
| Multi-swap (global Kawasaki) | m = 5 | 2.22 | — | m = 4 | 1.21 | — |
| Quantum, ordered ring + full phase | β 0.75, g 3 | 1.91 | 28% | β 0.5, g 3 | 1.39 | 56% |
| Quantum, ordered ring + ring phase (hardware-cheap) | β 0.75, g 1 | 1.80 | 22% | β 1.0, g 1 | 0.93 | 16% |
| Quantum, ring + full phase | β 0.75, g 1 | 1.64 | 9% | β 0.5, g 3 | 1.09 | 41% |
| Quantum, ring + linear phase (hardware target) | β 0.75, g 1 | 1.42 | 3% | β 1.0, g 1 | 0.55 | 3% |

The complete-mixer quantum proposal beats single swap in 100% (ETFs) / 84% (stocks) of
test windows. Per-window-best tuning (`mixer_test.py`) gave similar numbers: complete
2.68 / 2.08 vs tuned multi-swap 2.34 / 1.32, beating it in 89% / 88% of windows; mean jump
distance 2.58 / 2.51 swaps vs multi-swap 3.0 / 2.0.

### 5.3 Phase-off control (`phase_control.py`)

Same complete-mixer circuit with the score phase switched off:

| | ETFs | Stocks |
|---|---|---|
| Phase off (median gap ratio) | 1.84 | 1.05 |
| Phase on | 2.68 | 2.08 |
| Tuned multi-swap | 2.34 | 1.32 |
| Phase-off version beats multi-swap | 0% of windows | 17% |
| Phase improves the circuit | 100% of windows (median 1.46×) | 98% (median 1.90×) |

Conclusion: the gain over multi-swap is from score information in the circuit, not from
jump length.

### 5.4 Race to the optimum (`race.py`)

Attempts until a chain first sits on the best book S*, from matched random starts,
settings fixed from 5.2. Parallel tempering: 4 replicas at T × {1, 2.2, 4.6, 10}, swap
moves, adjacent exchanges, budget summed over replicas.

| Median attempts (score evaluations) | ETFs 6/6 | Stocks 6/6 | ETFs 8/8 | Stocks 8/8 |
|---|---|---|---|---|
| Locally balanced | 38 (1,140) | 12 (360) | 162 (9,072) | 66 (3,668) |
| **Single swap** | **179** | **100** | **1,093** | **452** |
| Quantum, complete + full | 184 | 125 | 1,264 | 890 |
| Parallel tempering | 199 | 139 | 1,405 | 887 |
| Multi-swap | 215 | 188 | 2,175 | 1,214 |

6/6: 32 test windows × 40 starts, budget 3,000; 8/8: 8 test windows × 24 starts, budget
15,000; ≥ 99% of runs solved. Single swap reaches S* in the fewest attempts and score
evaluations of all one-evaluation-per-step methods.

### 5.5 Hardware cost (`compile_depth.py`, `results/longshort_compile_depth.txt`)

Two-qubit gates / two-qubit depth after transpiling (optimization level 3, best of 3
seeds) onto FakeFez and FakeTorino:

| Variant | 11 qubits (6/6), Fez | 11 qubits, Torino | 15 qubits (8/8), Fez | 15 qubits, Torino |
|---|---|---|---|---|
| Ring mixer + linear phase | 83 / 63 | 56 / 56 | 122 / 104 | 116 / 104 |
| Ring mixer + ring phase | 115 / 84 | 79 / 61 | 141 / 107 | 145 / 111 |
| Ordered ring + ordered ring phase | 87 / 78 | 87 / 81 | 188 / 177 | 151 / 137 |
| Ring mixer + full phase | 241 / 127 | 237 / 138 | 428 / 240 | 413 / 198 |
| **Complete mixer + full phase** | **541 / 234** | **569 / 272** | **1,134 / 419** | **1,091 / 320** |

### 5.6 Real hardware (`experiments/hardware/`, `results/hardware/`)

ibm_marrakesh, 2026-11-15 UTC. 4 long / 4 short on the 8 core ETFs, window ending
2025-12-31 (3 local optima; greedy success 0.46; best book long SPY IWM IEF GLD, short EFA
EEM TLT DBC). Hardware-cheap circuit (ordered ring + ring phase, β 0.75, g 1), 86
two-qubit gates. All 35 starts × 1,024 shots in one SamplerV2 job (`dbsiephabdes73fr6n4g`),
dynamical decoupling on, **12 QPU-seconds** (pilot `dbsiegok09pc73b074jg`, 2 s; account
used 14 of 600 s).

| Metric | Hardware | Shots only | Ideal circuit | Single swap |
|---|---|---|---|---|
| Usable shots (exactly 4 long) | 43% | 100% | 100% | — |
| TVD to ideal proposals (valid outcomes, median) | 0.20 | 0.09 | 0 | — |
| Proposal-table asymmetry | 0.33 | 0.16 | 0 | — |
| Spectral gap of Metropolis chain | **0.043** | 0.088 | 0.090 | **0.061** |
| Stationary bias (TVD to target) | 0.048 | 0.062 | 0 | — |
| Chain probability of best book (target 0.231) | 0.208 | — | — | — |

The noisy simulator (FakeFez) predicted 77% usable shots; the device gave 43%.

---

## 6. What the result is good at, and what it is not

**Supported (claim these):**
- A real-data finance problem (market-neutral long–short book) whose landscape is
  genuinely rugged, with an exact answer key.
- In simulation, a score-informed quantum proposal (complete XY mixer + full phase)
  **samples / mixes faster** than single-swap and tuned multi-swap Metropolis on held-out
  windows, and the gain is attributable to the score phase (phase-off control).
- On real IBM hardware, the hardware-cheap circuit produces usable count-preserving
  proposals and the chain stays nearly unbiased.

**Not supported (do not claim):**
- Finding the best portfolio faster: single-swap Metropolis wins the race.
- Beating the best classical informed sampler per step: locally balanced swaps mix faster
  per attempt (but cost k(n−k) score evaluations per attempt; per evaluation plain swaps
  win).
- Any hardware advantage: the winning circuit (~540 two-qubit gates) cannot run usefully;
  on hardware the cheap circuit mixes slower than single swap.
- Any speedup in wall-clock time, or better investment performance.

**Mixing vs finding the optimum (why the two disagree):** the spectral gap measures how
fast a chain forgets its start and samples the whole target distribution (relaxation time
≈ 1/gap attempts). The race measures first arrival at the top. At low temperature single
swaps act like a downhill search with occasional backsteps, which arrives fast; long
jumps (multi-swap, quantum) help move *between* peaks but are usually rejected near the
top.

**Use cases for the sampling result:** robust positions under estimation noise (which
assets stay long or short across near-optimal books), offering several genuinely
different near-optimal books, counting near-ties, Bayesian model averaging, sensitivity
analysis. Caveat: temperature then needs a meaning (for example matched to estimation
noise); here it was a tuning choice (0.1 × std(S)).

**Pitch wording that matches the evidence:** "On a real-data, market-neutral long–short
portfolio problem with many competing near-optimal books, our score-informed quantum
proposal samples those books faster than classical swap-based MCMC, which helps
identify robust positions and genuinely different alternatives, not the single best book
faster. Shown in simulation; on today's hardware the noise erases the gain."

---

## 7. Methods and definitions

- **Single swap (local Kawasaki):** move one uniformly random long to short and one short
  to long. 1 score evaluation per attempt. The baseline (gap ratio 1).
- **Multi-swap (global Kawasaki):** pick j uniformly in 1..m, then a uniform book exactly j
  swaps away. 1 evaluation. "Tuned" = best m (fair tuning: one m from train windows).
- **Locally balanced informed swaps** (Zanella, JASA 2019, doi 10.1080/01621459.2019.1585255):
  propose a swap neighbour with probability ∝ sqrt(π(s')/π(s)) plus MH correction; costs
  k(n−k) evaluations per attempt. A naive heat-bath (∝ π) version mixes very poorly and was
  replaced; it is kept in code only for contrast.
- **Parallel tempering:** 4 single-swap replicas at T × {1, 2.2, 4.6, 10}, adjacent exchanges.
- **Quantum proposal:** section 4; Metropolis acceptance with exact scores.
- **Target distribution:** π(s) ∝ exp(S(s)/T), T = 0.1 × std(S) over valid books.
- **Spectral gap:** 1 − |λ₂| of the transition matrix, via the symmetrised matrix
  D^{1/2} P D^{−1/2} (all chains are reversible). Computed exactly by enumeration.
- **Landscape metrics:** local optimum = no single swap improves the score; greedy success
  = share of all starts from which steepest ascent ends at the global optimum.

---

## 8. Reproduce

```bash
source qiskit-env/bin/activate            # or create from requirements.txt
python -m pytest -q tests                 # 60 tests, offline
python -m qemcmc.data                     # data/instances.npz (prices cached in data/)
python -m qemcmc.longshort                # landscape + ring-mixer gaps, 6/6
python -m qemcmc.longshort --big          # 8/8 gaps, 2 windows per universe (~6 min)
PYTHONPATH=. python experiments/longshort/mixer_test.py     # ring vs complete vs ordered
PYTHONPATH=. python experiments/longshort/phase_control.py  # phase off vs on
PYTHONPATH=. python experiments/longshort/fair_tuning.py    # train/test, one setting each
PYTHONPATH=. python experiments/longshort/race.py           # race 6/6 (~10 s)
PYTHONPATH=. python experiments/longshort/race.py --n 16    # race 8/8 (~30-60 min)
PYTHONPATH=. python experiments/longshort/compile_depth.py  # transpiled gate counts
python -m qemcmc.hardware dry --backend fake_fez            # noisy dry run, no QPU
python -m qemcmc.hardware full --backend ibm_marrakesh --shots 1024   # uses ~12 QPU-s
python -m qemcmc.hardware analyze results/hardware/<file>.json
```

Hardware needs IBM credentials saved once with `python run_once.py` (reads `.env`; never
commit it).

## 9. File map

| Path | What |
|---|---|
| `qemcmc/data.py` | Prices, 64 windows, μ and Σ |
| `qemcmc/states.py` | Book numbering (rank, combo, bits, Qiskit int), swap neighbours |
| `qemcmc/objective.py`, `landscape.py`, `gaps.py`, `dial.py` | Original problem, landscape, gaps, dial |
| `qemcmc/circuits.py` | Qiskit proposal circuit, `score_terms`, statevector tables |
| `qemcmc/subspace.py` | Fast valid-subspace simulator, swap/multi-swap tables, informed proposals, Metropolis, gaps |
| `qemcmc/longshort.py` | Long–short score, h and J, landscape and gap runs |
| `qemcmc/hardware.py` | Hardware pipeline and analysis |
| `qemcmc/factors.py`, `hedgebook.py` | Negative pilots |
| `experiments/longshort/` | Winning-idea experiments and README |
| `experiments/hardware/README.md` | Hardware write-up |
| `experiments/landscape/`, `dial/`, `factor_pilot/`, `hedgebook/` | Path to the idea |
| `results/longshort_*`, `results/hardware/` | Raw outputs |

## 10. Commits and beads

Commits on `pilot/factor-selection`: `e2e6bcf` (long–short pilot), `471d3fb` (mixer
variants), `809b246` (compile depth, fair tuning, 6/6 race), `0583a18` (8/8 race,
confirmation write-up), `ab759a7` (hardware run), then this file. All on GitHub `main`.

Beads: `b3d` (long–short pilot), `kaa` (confirmation), `6nz` (hardware) closed. Open:
`0pc` (P3: re-tune β, g, T for hitting S*; 8/8 gap repeat on more windows), `17h` (P2: read
Monge 2020 in full), `k6c` (classical controls harness), `y5l`, `bld`.

## 11. Open questions and next steps

1. **Error mitigation on hardware:** about 586 QPU-seconds remain; rerun the 35-start
   table with gate twirling and readout mitigation (~15–30 s) to see how much mixing
   speed is recovered.
2. **8/8 spectral gaps on more windows** with the complete mixer (only 2 windows per
   universe so far, and those used the ring mixer).
3. **Tune for the race**, not mixing: β, g and T chosen on attempts-to-S*, annealed T,
   random per-step β/γ (Layden 2023). Unlikely to reverse the race result, untested.
4. **Hardware-feasible circuits that keep the gain:** smarter ring orderings, partial
   complete mixers (strongest pairs only), or the multi-qubit mixers in Hodson et al. 2019.
5. **Longer-range sampling use case:** define T from estimation noise and demonstrate a
   robustness analysis (position stability across sampled near-optimal books).

## 12. Key references

| Topic | Reference | DOI |
|---|---|---|
| QeMCMC mechanism | Layden et al. 2023, *Nature* | 10.1038/s41586-023-06095-4 |
| Optimisation framing | Marshall et al. 2026 (preprint) | 10.48550/arXiv.2602.06171 |
| No worst-case speedup | Orfi & Sels 2024, *PRA* | 10.1103/PhysRevA.110.052414 |
| Spread vs acceptance | Hsieh, Orfi & Sels 2026, *PRA* | 10.1103/x255-fw2l |
| Locally balanced proposals | Zanella 2019, *JASA* | 10.1080/01621459.2019.1585255 |
| Parallel tempering | Hukushima & Nemoto 1996, *JPSJ* | 10.1143/JPSJ.65.1604 |
| Long/short as spin glass | Galluccio, Bouchaud & Potters 1998, *Physica A* | 10.1016/S0378-4371(98)00332-X |
| Market mode | Plerou et al. 2002, *PRE* | 10.1103/PhysRevE.65.066126 |
| Closest quantum portfolio benchmark | Stopfer et al. 2025 (preprint) | 10.48550/arXiv.2509.17876 |
| Long/short XY mixers | Hodson et al. 2019 (preprint) | 10.48550/arXiv.1911.05296 |
| Fair benchmarking | Hellstern, Schacht & Zaefferer 2026 (preprint) | 10.48550/arXiv.2610.35126 |
