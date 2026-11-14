# Scope review

Critique of [`../project-scope.md`](../project-scope.md), grounded in the literature in
[`literature-review.md`](literature-review.md). Short verdict first, then answers to the five
critique questions, then sizing and hardware notes.

## Verdict

This is a well-scoped hackathon project. The research question is narrow and testable, the
classical baseline is the right one, and the scope already avoids the two traps that sink
most quantum-finance demos: claiming speedup, and mixing proposal efficiency with
end-to-end runtime. The literature supports the design almost point by point:

- The classical swap move is **Kawasaki dynamics** (Kawasaki 1966), the standard
  count-preserving MCMC move. Kawamata et al. (2026) benchmark count-preserving quantum
  proposals against exactly this baseline, in both a local (one swap) and a global (many
  swaps) form.
- Count-preserving XY circuits are well established (Hadfield 2019; Wang 2020) and have run
  on hardware for portfolio problems (He et al. 2023, 32 trapped-ion qubits).
- Measuring attempts to reach the optimum against an exact answer key is how Layden (2023)
  and Marshall (2026) report results.

The main risks are an easy problem landscape (question 1), an unmatched classical control
for the score-informed proposal (question 2), and hardware depth from the score phase
(question 3).

## Keep, change, drop

| Keep | Change | Drop or demote |
|---|---|---|
| Count-preserving swap vs. XY comparison | Make the circuit palindromic so proposals are symmetric and Metropolis is valid | 10 of 30 as a simulator case |
| Exact enumeration as answer key | Precompute the full proposal table at 8–16 qubits instead of running a circuit per step | Adaptive hardware chains |
| Best-so-far gap vs. attempts as the main chart | Report score evaluations alongside attempts | Asset visit counts as probabilities (fine as description only) |
| XY-only ablation | Add a heat-bath swap and greedy-with-restarts control | Full all-to-all score phase on hardware |
| Multi-swap control | Add a landscape-difficulty check per window | — |
| Separate hardware panel (shots, usable rate, time) | Use a hardware proposal table at 4 of 12 for an offline end-to-end replay | — |

## 1. Is 5 of 16 large enough, and why does the answer key matter?

**Size is not the issue; landscape is.** The metric is attempts, not wall-clock time, so a
4,368-state problem can still show differences in search behavior. What matters is whether
the swap landscape has multiple local optima. If a window has a single local optimum under
swaps, any descent method finds it almost immediately and no proposal can do much better.

Equal-weight mean–variance problems on liquid ETFs can be smooth. Graham & Craven (2020)
show local optima do occur in cardinality-constrained portfolio problems, but how many there
are depends on the data and on λ.

**Recommended check (cheap):** for every window, enumerate all portfolios and count local
optima under the swap neighborhood. At 5 of 16 that is 4,368 × 55 ≈ 240,000 score
evaluations, which takes seconds. Then:

- Report results for all windows, grouped by local-optimum count (1, 2–5, more than 5).
  Grouping avoids cherry-picking while showing where proposals matter.
- If almost every window has a single optimum, raise λ or add closely correlated ETF pairs
  (IEF/TLT, LQD/AGG). Near-duplicates create plateaus and competing optima.

**How to explain the answer key to judges.** Without it you can only say "method A found a
better score than method B." With it you can say how far each run is from the true best, how
often it finds the true best within budget, and how many attempts it took. The answer key
also allows an exact analysis no larger problem permits. With 4,368 states, you can build
each method's full transition matrix and compute its spectral gap, which measures how fast
the chain forgets where it started. That is the headline quantity in Layden et al. (2023).
A one-line pitch: "We picked a size where we know the right answer, so every claim is
measured, not estimated."

## 2. Which classical controls make the comparison convincing?

Swap Metropolis alone is necessary but not sufficient. The score-informed circuit uses
objective information when proposing, while the swap proposal is blind to it. Without a
classical control that is also informed, a quantum win could just mean "informed beats
blind." Recommended set, in priority order:

| Control | What it tests | Source |
|---|---|---|
| **Single swap Metropolis** (local Kawasaki) | Baseline | Kawasaki 1966; Kawamata 2026 |
| **Multi-swap Metropolis** (global Kawasaki: 1 to k swaps, uniform) | Whether gains come only from larger jumps | Kawamata 2026; Marshall 2026 (uniform multi-flip baseline) |
| **Heat-bath swap**: pick among all k(n−k) swaps with probability weighted by the Boltzmann factor | Informed classical proposal; costs k(n−k) score evaluations per step | Standard MCMC |
| **Greedy steepest descent with random restarts** | Whether any MCMC is needed | Chang et al. 2000; Shirai 2026 |
| **Simulated annealing with swaps** under the same temperature schedule | Standard portfolio heuristic | Crama & Schyns 2003; Kirkpatrick 1983 |

This is why the chart needs two x-axes, or two charts: **attempts** and **score
evaluations**. Heat-bath and greedy look strong per attempt but pay many score evaluations
per step. The quantum proposal pays circuit shots instead. Reporting both keeps the
comparison honest in each direction.

One more control is worth its cost because it is free at this size. Sample proposals from
the *classically computed* quantum proposal distribution. At 16 qubits this distribution can
be computed exactly on a laptop, so it isolates "this proposal shape helps" from "a quantum
device was needed." Say plainly in the pitch that at these sizes the second claim cannot
hold (Orfi & Sels 2024).

## 3. Is the score-informed XY circuit substantive? Is there a simpler one?

**Yes, the score phase is the substantive part.** Started from a single portfolio, an
XY-only circuit is a quantum walk over portfolios that ignores the score. Its proposals are
structured random multi-swaps. The score phase between mixing blocks is what lets the
proposal favor good portfolios. That is Layden's mechanism, and Shirai (2026) and Hsieh et
al. (2026) describe the trade-off it creates: proposals should reach distant portfolios
without jumping to much worse scores.

**Symmetry comes almost for free.** The XY generator and the diagonal score phase are both
real-symmetric. Applying them in a palindromic order (mix, phase, mix, with each mixing
block's gate order reversed in the second copy) makes the circuit equal to its own
transpose. Proposal probabilities are then symmetric, so the plain Metropolis rule gives a
valid sampler rather than a heuristic:

$$
U = M(\beta)\, P(\gamma)\, M(\beta)^{\text{rev}},
\qquad
U^{\top} = U
\;\Longrightarrow\;
\Pr(s \to s') = \Pr(s' \to s)
$$

Add a unit test that checks the proposal-probability matrix equals its transpose. On
hardware, noise and readout bias break the symmetry slightly; that is fine for an
optimization claim.

**Simpler circuits worth trying, in order of cost:**

1. **XY-only** (already planned): the ablation.
2. **Linear-only score phase:** keep only the single-asset terms of the score (each asset's
   return and own variance), which become single-qubit Z rotations with no two-qubit gates.
   It captures "prefer good assets" without "prefer good combinations." This is the best
   circuit for hardware.
3. **Nearest-neighbor score phase:** add pairwise covariance terms only for assets adjacent
   on the hardware ring. Order assets around the ring so that strongly correlated pairs are
   adjacent.
4. **Full score phase:** all pairwise covariance terms. At 12 qubits that is 66 pairwise
   terms, which needs many SWAP gates on the hardware layout. Simulation only.

**Ring or complete XY mixer.** A ring mixer only moves holdings between assets that are
neighbors on the ring, so asset order becomes a design choice; document it, or randomize it
per run. Heavy-hex IBM layouts contain 12-qubit rings, so a 12-asset ring mixer may map with
no SWAP gates. Check the coupling map of the assigned backend.

## 4. Is a hardware demo of the proposal step enough?

Yes, if it measures something the simulator cannot. The scope already rules out adaptive
hardware chains, and correctly so. Each step depends on the last measurement, so queue and
round-trip time dominate. Marshall et al. found one shot is nearly as slow as 10,000 once
overhead is included.

**Upgrade: a hardware proposal table at 4 of 12.** There are only 495 valid starting
portfolios. Run the proposal circuit once from each, with a few hundred shots, in a single
batch. That yields a hardware-measured proposal distribution for every state. Then run the
full search offline, drawing each proposal from the measured outcomes of the current state.
The result is an end-to-end chain driven entirely by real hardware proposals, with no
round trips. From the same data:

- usable proposal rate (right holding count) per start;
- distance between hardware and ideal proposal distributions, per start;
- the spectral gap of the hardware-driven chain against the ideal chain.

**Budget.** The Open Plan allows 10 minutes of QPU time per 28-day rolling window. 495
circuits × 256 shots is about 127,000 shots, which is plausibly a minute or two of QPU time,
but this is an estimate. Run a small pilot job first and measure the time it uses before
committing. If the full table does not fit, fall back to the planned batch from a few fixed
starts.

## 5. If the classical baseline wins, what still makes the project interesting?

A negative result is the expected outcome at these sizes (Orfi & Sels 2024; Hellstern et al.
2026). Plan diagnostics that explain *why*, so the project still teaches something:

- **Landscape explanation:** local-optimum counts per window. If classical wins mostly on
  single-optimum windows, that is a finding about the problem, not a failure.
- **Jump-distance profile:** for accepted proposals, how many assets changed. Does the score
  phase produce longer accepted jumps than single swaps, as Layden and Shirai predict?
- **Evolution-time sweep:** success against mixing time. Hsieh et al. (2026) predict an
  optimum, with too little mixing behaving like local moves and too much like random jumps.
  Showing that curve on real portfolio data is a clean result.
- **Exact spectral gaps** for every method at 8, 12 and 16 assets: a rigorous mixing
  comparison independent of run noise.
- **Hardware fidelity:** usable rate and distance from ideal, which quantify how far current
  devices are from the simulated proposal.
- **Cost per useful proposal:** shots and seconds per accepted move, against score
  evaluations for classical controls.

## Sizes and simulation

Two facts change the size table.

**At 16 qubits or fewer, precompute the proposal table.** For a fixed window and fixed
circuit parameters, the proposal distribution from each valid portfolio never changes.
Simulate the circuit once per valid portfolio (4,368 small statevector runs at 5 of 16), keep
the probabilities, and every chain step becomes a table lookup. Thousands of chains then cost
almost nothing, and the same table gives the spectral gap. The table is a 4,368 × 4,368
matrix of probabilities, about 150 MB, which fits easily in 24 GB.

**The holding count limits which states can occur.** XY gates and the score phase never
change the holding count, so an ideal simulation only needs the valid portfolios, not all
2ⁿ bit strings. A custom simulator restricted to valid portfolios needs far less memory.

| Holdings | Valid portfolios | Single swaps per state | State vector, all bit strings | State vector, valid portfolios only | Recommendation |
|---|---|---|---|---|---|
| 3 of 8 | 56 | 15 | 4 KB | <1 KB | Table; sanity check and hardware fallback |
| 4 of 12 | 495 | 32 | 64 KB | 8 KB | Table; hardware proposal table |
| 5 of 16 | 4,368 | 55 | 1 MB | 70 KB | Table; **main benchmark** |
| 6 of 20 | 38,760 | 84 | 16 MB | 620 KB | Per-step statevector (milliseconds); **promote to secondary benchmark** |
| 8 of 24 | 735,471 | 128 | 256 MB | 12 MB | Per-step run takes roughly a second; only short runs on a few windows |
| 10 of 30 | 30,045,015 | 200 | 16 GiB | 480 MB | Drop as a simulator case; a valid-portfolio simulator would fit but is too much code for 24 h |
| 10 of 50 | 10.3 billion | 400 | — | — | Classical-only extension; certify the optimum with a MIQP solver |

Enumeration stays cheap through 8 of 24 (735,471 score evaluations), so 6 of 20 also has an
exact answer key. That makes it a stronger secondary benchmark than the scope assumes.

## Data choices still open

- **Basket.** Keep the 8-ETF core. To reach 12, 16 and 20 assets, add liquid ETFs with long
  histories that bring both new exposures and near-duplicates. Candidates: VNQ, TIP, LQD,
  HYG (for 12); XLE, XLK, XLV, EWJ (for 16); XLF, XLU, AGG, SLV (for 20). Verify each
  inception date. DBC and HYG start in 2006–2007, which sets the earliest window.
- **Windows.** Rolling 252-day windows ending each quarter from 2010 to 2025 give about 60
  instances, enough to report medians and spreads across windows.
- **Risk penalty λ.** Choose λ so the return and variance terms have similar spread across
  the valid portfolios, or sweep a small set such as 1, 3 and 10. Report how λ changes the
  local-optimum count; it is the main knob for landscape difficulty.
- **Estimation noise.** Expected-return estimates from one year of data are very noisy
  (Chopra & Ziemba 1993; Merton 1980). That is acceptable here, because the claim is about
  search on a fixed objective, not about investment performance. Say so in the pitch.
