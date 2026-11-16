# Development guide — QeMCMC portfolio search

Single entry point for developers and coding agents. It condenses
[`project-scope.md`](project-scope.md) and everything in [`research/`](research/README.md)
into what you need to build. When this file and a source disagree, the source wins; fix this
file.

- Task tracking: `bd` (beads). Run `bd prime`, then `bd ready`. Do not keep TODO lists in
  markdown.
- Git policy: conservative. No commits or pushes unless the user asks.

---

## 1. What we are building (one paragraph)

A benchmark for a 24-hour IBM Quantum hackathon. Choose exactly k of n ETFs, equal weight,
to maximize a mean–variance score. Compare a classical swap-based Metropolis search against
a search whose proposals come from a count-preserving quantum circuit (XY mixer plus a score
phase). The question: does the quantum proposal reach the best portfolio in **fewer
attempts**, and what does it cost in **shots and runtime**? Small sizes are chosen so the
true optimum is known by enumeration (the "answer key").

**The claim is proposal efficiency on a fixed objective.** Not a quantum speedup, not
investment performance. A classical win is the expected outcome; the diagnostics in §8 make
that result informative.

---

## 2. Glossary

| Term | Meaning |
|---|---|
| Portfolio / state | Bit string x of length n with exactly k ones. Bit i = 1 means ETF i is held. |
| Valid portfolio | Any bit string with exactly k ones. There are C(n, k). |
| Swap | Exchange one held ETF for one unheld ETF. k(n−k) swaps per state. Also called **local Kawasaki dynamics**. |
| Multi-swap | 1 to m swaps at once, chosen uniformly. **Global Kawasaki dynamics.** |
| Attempt | One proposal, accepted or not. Wrong-count hardware outcomes still count as an attempt. |
| Score evaluation | One call to S(x). Tracked separately from attempts. |
| Answer key | Optimum S\* per window, found by full enumeration. |
| Gap | S\* − best-so-far score. Main y-axis. |
| Proposal table | Matrix Q where Q[s, s′] = probability the proposal from s yields s′. Precomputed for n ≤ 16. |
| Usable rate | Fraction of hardware shots with exactly k ones. |
| Palindromic circuit | Mix, score phase, mix with gate order reversed. Makes Q symmetric. |

---

## 3. Objective and acceptance

Inputs per window: annualized mean returns μ (length n), covariance Σ (n × n), risk penalty
λ. Equal weights w = x / k. The score to **maximize** is:

$$
S(x) = \frac{1}{k}\,\mu^\top x \;-\; \frac{\lambda}{k^2}\, x^\top \Sigma x,
\qquad \sum_i x_i = k
$$

Energy E(x) = −S(x). Metropolis acceptance at temperature T:

$$
A(x \to x') = \min\!\Big(1,\; e^{-\left(E(x') - E(x)\right)/T}\Big)
$$

No count penalty is needed: every proposal (ideal circuit or classical) keeps k holdings.
If a hardware outcome has the wrong count, record the attempt and keep the current
portfolio.

---

## 4. Invariants (test these)

1. Every classical and ideal-circuit proposal has exactly k ones.
2. The palindromic proposal table is symmetric: Q equals its transpose (to numerical
   tolerance). This is what makes plain Metropolis valid. Unit-test it.
3. Every row of Q sums to 1 and has support only on valid portfolios.
4. All methods share the same data, score function, starting portfolios, temperature
   schedule and attempt budget for a given run.
5. Enumeration optimum is ≥ every score any method reports.
6. Attempts, score evaluations, shots and wall-clock time are logged as separate fields.
   Never combine them into one "speed" number.

Hardware noise breaks invariant 2 slightly. That is acceptable for the optimization claim;
report it, don't hide it.

---

## 5. Methods to implement

### 5.1 Classical controls (priority order)

| Control | Proposal | Score evals per step | Purpose |
|---|---|---|---|
| Swap Metropolis (local Kawasaki) | Uniform random single swap | 1 | Baseline |
| Multi-swap Metropolis (global Kawasaki) | 1 to m swaps, uniform | 1 | Are gains just from bigger jumps? |
| Heat-bath swap | Choose among all k(n−k) swaps, weighted by Boltzmann factor | k(n−k) | Informed classical proposal; the fair match for the score-informed circuit |
| Greedy steepest descent + random restarts | Best improving swap; restart at local optimum | k(n−k) | Is MCMC needed at all? |
| Simulated annealing with swaps | Single swap, same schedule | 1 | Standard portfolio heuristic |
| Classical sampling of the ideal quantum Q | Draw from the precomputed table | 1 | Separates "this proposal shape helps" from "a quantum device was needed" |

### 5.2 Quantum proposals

All start from the current portfolio as a computational basis state (no Dicke-state prep).
One qubit per ETF.

| Variant | Score phase | Two-qubit gates in phase | Use |
|---|---|---|---|
| XY-only | none | 0 | Ablation; structured random multi-swap |
| Linear-only | Single-asset terms only (each asset's return and own variance) as Z rotations | 0 | **Best for hardware** |
| Nearest-neighbor | Linear + covariance terms for ring-adjacent assets | n on a ring | Hardware stretch; order the ring so correlated pairs are adjacent |
| Full | All pairwise covariance terms (66 at n = 12) | n(n−1)/2 | Simulation only |

Circuit shape (palindromic, so the circuit is its own transpose):

$$
U = M(\beta)\, P(\gamma)\, M(\beta)^{\text{rev}}
$$

M is a block of XY gates (ring or complete graph); M^rev applies the same gates in reverse
order; P is the diagonal score phase. Both generators are real-symmetric, so U equals its
transpose and Pr(s → s′) = Pr(s′ → s).

Design notes:

- **Ring vs. complete mixer.** Ring maps to hardware with no SWAPs (heavy-hex devices
  contain 12-qubit rings; check the assigned backend's coupling map). Ring makes asset order
  a design choice: document it or randomize it per run.
- **Scale.** Layden normalizes problem and mixer terms by the ratio of their Frobenius
  norms, and draws mixing weight and evolution time at random per step. Consider the same,
  and also sweep them (see §8).
- Credit Layden et al. (2023) for the mechanism and Marshall et al. (2026) for the
  optimization framing.

---

## 6. Sizes and how to simulate each

| Holdings | Valid portfolios | Swaps per state | Strategy | Role |
|---|---|---|---|---|
| 3 of 8 | 56 | 15 | Proposal table | Sanity check; hardware fallback |
| 4 of 12 | 495 | 32 | Proposal table | **Hardware target** (full hardware proposal table) |
| 5 of 16 | 4,368 | 55 | Proposal table (≈150 MB float64) | **Main benchmark** |
| 6 of 20 | 38,760 | 84 | Per-step statevector (ms each) | **Secondary benchmark**; still has exact answer key |
| 8 of 24 | 735,471 | 128 | Per-step statevector (~1 s each) | Short runs on a few windows only |
| 10 of 30 | 30,045,015 | 200 | — | **Dropped** as a simulator case |
| 10 of 50 | ≈10.3 billion | 400 | Classical only; certify with a MIQP solver | Motivation / extension |

**Proposal table method (n ≤ 16).** For a fixed window and fixed circuit parameters the
proposal distribution from each state never changes. Simulate once per valid portfolio,
store Q, and every chain step is a table lookup. The same Q gives exact spectral gaps.

**Count-restricted simulation.** XY gates and the score phase preserve the holding count,
so a simulator restricted to the C(n, k) valid states needs far less memory than 2ⁿ. Worth
it only if 6 of 20 or 8 of 24 per-step runs are too slow.

---

## 7. Data

- **Core basket (8):** SPY, IWM, EFA, EEM, IEF, TLT, GLD, DBC.
- **Candidates to extend** (verify each inception date):
  - to 12: VNQ, TIP, LQD, HYG
  - to 16: XLE, XLK, XLV, EWJ
  - to 20: XLF, XLU, AGG, SLV
  Include near-duplicates (IEF/TLT, LQD/AGG) on purpose: they create plateaus and competing
  optima.
- **Source:** adjusted daily closes via `yfinance`.
- **Windows:** rolling 252-trading-day windows ending each quarter, 2010–2025 (about 60
  instances). DBC and HYG start 2006–2007, which bounds the earliest window.
- **λ:** pick so return and variance terms have similar spread across valid portfolios, or
  sweep {1, 3, 10}. λ is the main knob for landscape difficulty; report its effect.
- **Estimation noise** (Chopra & Ziemba 1993; Merton 1980) is acceptable because the claim
  is about search on a fixed objective. Say so in the pitch. Ledoit–Wolf shrinkage is an
  optional covariance choice.

---

## 8. Experiments and outputs

### 8.1 Do first: landscape check

For every window (and λ), enumerate all valid portfolios and count **local optima under the
swap neighborhood**. At 5 of 16 that is about 240,000 score evaluations: seconds.

- Group all results by local-optimum count: 1, 2–5, more than 5. Report every window; the
  grouping avoids cherry-picking.
- If nearly every window has a single optimum, raise λ or add correlated ETF pairs before
  running anything else. On a one-optimum landscape no proposal can beat descent by much.

**Result (2026-11-14; our own finding, literature-checked in bead `5xy`).** The
landscape is almost always single-peaked. At 5 of 16 with λ = 1, 3, 10, all 64 windows
have exactly one local optimum and steepest ascent reaches S\* from every start. Raising
λ, shrinking μ, 63/126-day windows, individual stocks and an SPY hedge do not change this
while returns are kept (at most 2–5 optima in any window). Cause: the common market factor
makes most pairs positively correlated, and node terms are about 13× larger than edge
terms. Random correlations without a market factor give a median of 12 optima. Evidence:
`experiments/landscape/README.md` and the `ieo` bead notes.

Literature (see `research/references.md`, "Landscape structure"): the market mode is the
largest eigenvalue of asset correlations (Plerou et al. 2002). Stopfer et al. (2025)
independently find variance-minimizing portfolio problems harder for classical solvers
than return-maximizing ones, and that exact MIP solves real instances up to 1,000 assets
in seconds. No paper found that reports single-peaked swap landscapes for equal-weight
selection; Monge (2020) studies the same problem class via factor models and should be
read in full. The M♮-concavity theorem (swap optimum is global) does not explain it: our
data violate its exchange condition.

**Framing (bead `lhr`, adopted 2026-11-14; reopen the bead if you object).** Keep the objective in
§3 unchanged. Main benchmark at λ = 3 (returns lead) and λ = 30 (most rugged setting where
returns still matter: 20% of windows have 2–3 optima, returns change the optimum in 88%).
Measure attempts and score evaluations to reach S\* (or within a tolerance), not escape
from local optima. The linear-only hardware circuit then encodes nearly the whole
objective. A secondary, simulation-only "difficulty dial" removes the market component
from Σ step by step (bead `t3h`) to show where longer quantum jumps start to pay off.

### 8.2 Main result

- **Chart:** best-so-far gap vs. attempts, median and spread across matched runs and
  windows. Make a second chart (or second x-axis) against **score evaluations**: heat-bath
  and greedy look strong per attempt but pay k(n−k) evaluations per step.
- **Table:** success rate (hit S\*) within budget, attempts, score evaluations, runtime.

### 8.3 Diagnostics (keep a negative result informative)

| Diagnostic | What it shows | Literature hook |
|---|---|---|
| Local-optimum counts per window | Whether classical wins are a landscape effect | Graham & Craven 2020 |
| Jump-distance profile of accepted moves | Does the score phase produce longer accepted jumps than swaps? | Layden 2023; Shirai 2026 |
| Evolution-time / mixing-angle sweep | Expected optimum: too little mixing ≈ local moves, too much ≈ random jumps | Hsieh, Orfi & Sels 2026 |
| Exact spectral gap per method at 8, 12, 16 assets | Mixing comparison free of run noise | Layden 2023 |
| Acceptance rate | Tracks spectral gap; usable as a tuning signal | Nakano et al. 2024 |
| Hardware fidelity: usable rate, distance from ideal Q | How far the device is from the simulated proposal | — |
| Cost per useful proposal | Shots and seconds per accepted move vs. score evals for classical | Hellstern et al. 2026 |

**Result: exact spectral gaps (2026-11-14, `python -m qemcmc.gaps`, bead `cnc`).** Ring
XY mixer, palindromic circuit, every 8th window, T = 0.3 × std(S), phase angle g / std(S).
On real data the quantum proposal mixes **slower** than uniform single swaps per attempt:

| Size | λ | Best setting | Gap vs swap (median over windows) | Range |
|---|---|---|---|---|
| 4 of 12 | 30 | β = 1.0, full phase | 0.73 | 0.27–0.81 |
| 5 of 16 | 3 | β = 1.0, full phase, g = 30 | 0.55 | 0.32–0.75 |
| 5 of 16 | 30 | β = 1.0, full phase, g = 3 | 0.80 | 0.30–0.98 |
| 5 of 16 | 30 | β = 1.0, linear phase, g = 30 | 0.67 | 0.44–0.97 |

The circuit rarely re-proposes the current portfolio (2–7%); it proposes longer jumps that
a single-peaked landscape mostly rejects (spread vs. acceptance, Hsieh, Orfi & Sels 2026).
The complete mixer is worse than the ring. Linear-only is close to full, so the hardware
circuit loses little. Consistent with §1: a classical win, now explained. Outputs:
`results/gaps_n12_k4.csv`, `results/gaps_n16_k5.csv`.

### 8.4 Hardware plan (4 of 12)

1. Transpile the linear-only (or nearest-neighbor) palindromic circuit with a ring XY mixer
   onto a 12-qubit ring of the assigned backend. Record compiled depth and two-qubit count.
2. **Pilot first.** Run a small job and measure the QPU time it actually uses. The Open
   Plan allows **10 QPU-minutes per 28-day rolling window**. Which execution modes the Open
   Plan permits was not confirmed; check before planning a session.
3. If budget allows: run the circuit from all 495 starting portfolios (~256 shots each,
   ≈127,000 shots) in one batch. This gives a **hardware-measured proposal table**.
4. Replay full searches offline, drawing each proposal from the measured outcomes of the
   current state. End-to-end chains with real hardware proposals and no round trips.
5. Report: usable rate per start, distance from ideal per start, spectral gap of the
   hardware chain vs. the ideal chain, shots, elapsed time.
6. Fallback if the table does not fit: a batch of proposals from a few fixed starts, paired
   with the same circuits in simulation.

**Do not** run adaptive hardware chains (each step depends on the last measurement, so
queue and round-trip time dominate; Marshall et al. found one shot per step nearly as slow
as 10,000).

---

## 9. Suggested build order

File these as beads; this is sequencing guidance, not a task list.

1. Data loader → μ, Σ per window; score function; enumeration answer key.
2. Landscape check (§8.1). Decide λ and basket from it.
3. Classical controls (§5.1) with a shared run harness and logging of all cost fields.
4. Proposal-table builder for XY-only and linear-only circuits; symmetry unit test.
5. Table-driven chains; main chart at 5 of 16.
6. Spectral gaps, jump-distance profile, evolution-time sweep.
7. Hardware pilot, then the 4 of 12 hardware proposal table and offline replay.
8. Stretch: 6 of 20 per-step simulation; nearest-neighbor and full score phases.

---

## 10. Repository and environment

Done: build-order steps 1–2 (data, score, answer key, landscape check), step 4 (proposal
circuits, symmetry test, fast proposal tables) and the spectral-gap part of step 6. Run commands are
in `CLAUDE.md` / `AGENTS.md` under Build & Test.

| Path | Purpose |
|---|---|
| `qemcmc/data.py` | Downloads adjusted closes for the 20 ETFs (2008-12 to 2025-12) to `data/prices.csv`; builds 64 quarterly 252-day windows of annualized μ and Σ in `data/instances.npz`. `load_instances(n)` returns the first n tickers (baskets are nested prefixes, core 8 first). |
| `qemcmc/states.py` | `StateSpace(n, k)`: every valid portfolio has a rank (lexicographic), combo, 0/1 vector and integer. The integer matches Qiskit measurement keys (qubit i = ETF i, `int(key, 2)`). `swap_neighbors()` gives the k(n−k) single-swap neighbors of each rank. Index proposal tables and chains by rank. |
| `qemcmc/objective.py` | `score()` and `enumerate_scores()` for S(x); writes `results/answer_key_n{n}_k{k}.csv` (S\*, optimal portfolio, tie count, gap to second best) for 3/8, 4/12, 5/16, 6/20 at λ = 1, 3, 10. |
| `qemcmc/landscape.py` | Local optima under swaps, group (1, 2–5, >5), greedy success per window; writes `results/landscape_n{n}_k{k}.csv`. `select_windows()` picks a stratified window subset. |
| `qemcmc/circuits.py` | Qiskit proposal circuit U = M P M^rev: `proposal_circuit()` (mixer ring/complete; phase none/linear/ring/full; ring order), `score_terms()` (node h, edge J), `proposal_table()` (exact Q by statevector; slow beyond 12 qubits). Use this circuit for hardware. |
| `qemcmc/subspace.py` | Fast count-restricted simulator, tested equal to the Qiskit tables: `mixer_matrix()` (once per β), `proposal_table_fast()` (≈1 s at 5 of 16), `swap_table()`, `metropolis_matrix()`, `spectral_gap()`. |
| `qemcmc/gaps.py` | Spectral-gap sweep per method; writes `results/gaps_n{n}_k{k}.csv`. |
| `experiments/landscape/` | One-off scripts behind the §8.1 result. |
| `tests/` | Offline tests (synthetic data). |
| `requirements.txt` | Pinned env: qiskit 2.6.2, qiskit-aer 0.18.2, qiskit-ibm-runtime 0.52.1, yfinance 1.8.0, pytest, numpy, scipy, pandas, matplotlib, seaborn |
| `qiskit-env/` | Local virtualenv |
| `run_once.py` | Saves IBM credentials from `.env` (`IBM_API_KEY`, `IBM_CRN`) as the default account. Run once. |
| `backend.py` | Creates `QiskitRuntimeService()` |
| `*.ipynb` | Hackathon starter notebooks |
| `docs/` | Scope, research, this file |

Data conventions: simple daily returns; μ = 252 × mean, Σ = 252 × covariance; window =
last 252 returns on or before each quarter end, 2010Q1–2025Q4. No risk-free rate (with
equal weights it shifts every score by the same constant). Never commit `.env` or
credentials.

---

## 11. Positioning and claims

**Closest prior work:** Kawamata, Nakano & Fujii (2026, *Phys. Rev. Applied*) already build
count-preserving MCMC proposals from XY-mixer circuits and beat local and global Kawasaki
dynamics (autocorrelation ≈14× and ≈7.7× faster); Kawamata & Fujii (2026, preprint) ran it
on IBM Heron r2 using neural-network surrogates. **Our difference:** a direct circuit
proposal per step, real financial data, exact answer key.

Do **not** claim:

- A quantum speedup at any simulated size (Orfi & Sels 2024 bound rules out a speedup for
  any unital proposal in the worst case; Hellstern et al. 2026).
- Better out-of-sample portfolios. We measure search efficiency only.
- That Marshall's or Kawamata's results transfer directly.
- That asset visit counts are probabilities, unless proposals are symmetric and chains have
  demonstrably mixed.

Pitch line for the answer key: *"We picked a size where we know the right answer, so every
claim is measured, not estimated."*

---

## 12. Key references

Full annotated list with DOIs and OpenAlex IDs: [`research/references.md`](research/references.md);
BibTeX: [`research/references.bib`](research/references.bib).

| Topic | Reference | DOI |
|---|---|---|
| QeMCMC mechanism | Layden et al. 2023, *Nature* | 10.1038/s41586-023-06095-4 |
| Optimization framing, hardware overhead | Marshall et al. 2026 (preprint) | 10.48550/arXiv.2602.06171 |
| Closest prior work | Kawamata, Nakano & Fujii 2026, *PR Applied* | 10.1103/qprn-rs96 |
| Speedup bound | Orfi & Sels 2024, *PRA* | 10.1103/PhysRevA.110.052414 |
| Spread vs. acceptance trade-off | Hsieh, Orfi & Sels 2026, *PRA* | 10.1103/x255-fw2l |
| Symmetric QAOA proposals | Nakano et al. 2024, *PRR* | 10.1103/PhysRevResearch.6.033105 |
| XY mixers | Wang et al. 2020, *PRA* | 10.1103/PhysRevA.101.012320 |
| XY portfolio on hardware | He et al. 2023, *npj QI* | 10.1038/s41534-023-00787-5 |
| Swap move origin | Kawasaki 1966, *Phys. Rev.* | 10.1103/PhysRev.145.224 |
| Portfolio heuristics | Chang et al. 2000, *Comput. Oper. Res.* | 10.1016/S0305-0548(99)00074-X |
| Fair benchmarking | Hellstern, Schacht & Zaefferer 2026 (preprint) | 10.48550/arXiv.2610.35126 |
| Quantum portfolio benchmark (closest classical-vs-quantum study) | Stopfer et al. 2025 (preprint) | 10.48550/arXiv.2509.17876 |
| Market mode in correlations | Plerou et al. 2002, *PRE* | 10.1103/PhysRevE.65.066126 |

Read depth matters: only Layden 2023 and Marshall 2026 were read in full; the rest are
abstract or metadata only (see `references.md`).
