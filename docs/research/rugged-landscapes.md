# Rugged landscapes

Why the 5-of-16 ETF problem has one peak, which finance problems with exactly k holdings can
have many, and how to tell them apart before running QeMCMC. Written after the landscape
finding in `../DEVELOPMENT.md` §8.1 (every window single-peaked).

Citations use (Author Year); full entries are in [`references.md`](references.md), in the
section *Rugged landscapes*. **[full]**, **[abs]** and **[meta]** have the same meaning as
in [`literature-review.md`](literature-review.md). Claims marked **(ours)** are our own
reasoning from the cited work, not published results.

## Summary

- **One peak is the expected result, not a data problem.** Each ETF's return and variance
  are about 13× larger than the pair terms, so the score nearly sorts assets by their own
  value. A score that is a pure sum of per-asset values has exactly one swap-local optimum.
- **QeMCMC needs the opposite regime.** Every reported gain is on frustrated, dense,
  low-temperature landscapes whose best states score almost the same but are far apart
  (Layden 2023 [full]). No paper applies QeMCMC to portfolio selection (searched
  November 2026).
- **Removing the market mode is a weak dial (ours).** With exactly k holdings, a market
  factor shared equally by all assets adds the same amount to every portfolio. Keep it as
  an ablation.
- **The main dial is r**, the spread of the pair terms divided by the spread of the
  per-asset terms. Many optima should appear only once r is about 1 or larger (ours).
- **Best candidates:** minimum variance on a mixed-asset ETF universe; market-neutral
  long/short with fixed long and short counts; least-correlated-k selection; credit-scoring
  feature selection.
- **Baseline to beat:** parallel tempering with swap moves, not only plain swap
  Metropolis.

## 1. The score as a graph

The score for equal weights wᵢ = xᵢ / k is μ · w − λ wᵀΣw. Because xᵢ² = xᵢ for 0/1
holdings, it splits into one term per asset and one term per pair:

| Part | Value | Meaning |
|---|---|---|
| Node i (one per ETF) | hᵢ = μᵢ/k − λΣᵢᵢ/k² | The asset's return minus its own variance |
| Edge i–j (one per pair) | −2λΣᵢⱼ/k² | Shared risk only; no return term |

The score of a portfolio is the sum of its held nodes plus the sum of its held pairs. Profit
sits only on the nodes, because return is linear in the weights. Risk is split: own
variance on the nodes, co-movement on the edges. With 16 ETFs there are 120 edges.

- Σᵢⱼ > 0 (the pair moves together): the edge is a penalty for holding both.
- Σᵢⱼ < 0 (the pair moves opposite): the edge is a reward, because they hedge.

This graph is not the search graph. In the search graph each node is a whole portfolio
(4,368 of them) and each edge is one swap (55 per portfolio). "Local optimum under swaps"
refers to the search graph. The asset graph sets its shape.

### Why one peak follows

If the edges were zero, the score would be a sum of node values and the top-k set would be
the only swap-local optimum: any other set holds some asset i and omits some j with
hⱼ > hᵢ, and swapping them improves the score. Edges can only create other optima if their
spread is comparable to the spread of the nodes. That gives the ratio

$$
r = \frac{(\lambda/k^2)\cdot \mathrm{spread}_{i<j}(\Sigma_{ij})}{\mathrm{spread}_i(h_i)}
$$

Spread (not mean) is what matters, because a constant added to every edge changes every
portfolio's score by the same amount when exactly k assets are held. Our windows sit far
below r = 1. The threshold r ≈ 1 is our inference from this argument, not a published
constant, so it has to be measured (E0 and E1 below).

### Why removing the market mode does little (ours)

Under a one-factor model, Σ = σₘ²ββᵀ + D. The pair part becomes σₘ²(β · x)², a function of
one number, the portfolio's total market exposure. If all betas were equal, β · x = kβ̄ for
every valid portfolio, so the factor adds a constant. Only differences in beta survive, and
they pull every portfolio toward the same low-beta group, which gives one basin rather than
competing ones.

### Published evidence agrees

- On OR-Library equity instances (Hang Seng to S&P 100), swap search found 1 to 5 local
  minima, and the global optimum's basin covered 30–60% of the search space. The author
  calls this "a common feature in financial market related instances" (di Tollo 2015 [full]).
- The same paper builds an artificial covariance of hedged pairs (correlations −1 and −0.9).
  There every hedged pair is a local optimum and the global basin shrinks as 1/n.
- Quantum portfolio papers used small single-market stock sets (Hodson 2019: 8 ASX stocks;
  Brandhofer 2022: likely DAX 30) and report no landscape structure.

## 2. What QeMCMC needs

- **Mechanism.** Proposals that are far in Hamming distance but close in score, so jumps
  between distant minima are still accepted (Layden 2023 [full]).
- **Size of the effect.** On fully connected SK instances at T = 1, the spectral gap scaled
  as about 2^(−0.264n) for the quantum proposal, against 2^(−0.94n) for single flips and
  2^(−0.948n) for uniform proposals (Layden 2023 [full]). The gain held only at T ≲ 1.
- **What removes it.** Sparse, less frustrated 1D instances shrank it; a quantum proposal
  built on the wrong landscape did no better than uniform (Layden 2023 [full]).
- **Limits.** No speedup on worst-case unstructured problems, and proposals that fully
  thermalize reduce to uniform (Orfi & Sels 2024a, 2024b [abs]). Part of the gain can be
  reproduced by a classical tensor-network emulation of the quantum proposal
  (Christmann 2025 [abs]).
- **Closest constrained work.** XY-mixer proposals with a fixed number of ones beat local
  and global Kawasaki (swap) dynamics by about 14× and 7.7× in autocorrelation decay in
  simulation, and 12.3× and 5.2× on IBM hardware at N = 1064. That is one instance at one
  temperature, and mixing degraded at lower temperature (Kawamata 2026a, 2026b [abs]).

A single-peaked landscape removes everything the quantum proposal exploits.

## 3. Candidate formulations

Ranked by expected ruggedness under swaps, fit to an exact-k quadratic encoding at
n ≈ 12–20, and reuse of the existing pipeline. The ranking is ours. No paper counts swap
local optima for any of these at this size, so each must pass the screen in §5 first.

| Rank | Formulation | Where frustration comes from | Size | Evidence | Main risk |
|---|---|---|---|---|---|
| 1 | Minimum variance (μ = 0), or μ shrunk, on a mixed-asset 16-ETF universe | Hedge pairs reward holding both; redundant pairs penalize it | 4,368 states at 5 of 16 | Mechanism plus di Tollo's hedged-pair instance | Stock–bond correlation sign changes across periods |
| 2 | Market-neutral long/short with exactly k_L longs and k_S shorts | Pair effect flips sign with position side | 2,970 at 2+2 of 12; 160,160 at 3+3 of 16 | Strongest theory (Galluccio 1998) | Theory is for continuous weights, not exact-k swaps |
| 3 | Least-correlated k / max-diversification / k-independent set on a correlation graph | The count constraint forces competition among many penalties | 4,368 at 5 of 16 | Large heuristic literature; densest-k-subgraph hard to approximate | Small-n optima counts unknown |
| 4 | Credit-scoring feature selection (German Credit, 6 of 20) | Relevance vs redundancy | 38,760 states | Several quantum QUBO papers | Plain mutual-information version has same-sign pair terms; may be smooth |
| 5 | Planted factor-neutral basket (Wishart-style) | Number of factors per asset | Any n | Easy–hard–easy profile (Hamze 2020) | Adaptation to exact k untested; planted structure can leak (Li 2026) |
| 6 | k-medoids stress-scenario selection; p-median branch or ATM siting | Each item served by its nearest chosen site | Needs extra qubits or higher-order terms | Strongest classical multi-optima evidence | Simulation only |

### Rank 1: minimum variance on mixed assets

Setting μ = 0 is cardinality-constrained minimum variance, a standard choice for an
investor who distrusts noisy mean estimates (Chopra & Ziemba 1993; Merton 1980). Shrinking
μ toward its average, or raising λ, is the continuous version of the same dial. The
universe matters more than removing the market: a mixed set such as SPY, EFA, EEM, IWM,
TLT, IEF, SHY, TIP, LQD, HYG, GLD, SLV, DBC, UUP, VIXY and VNQ adds hedge pairs like di
Tollo's artificial instance. Correlation signs for this list are not verified; check them
per window.

### Rank 2: long/short

**Long** means owning the asset; you gain when it rises. **Short** means borrowing and
selling it; you gain when it falls. In the model a long has weight +1/k_L, a short −1/k_S,
and an unheld asset 0. A 6-long/6-short book buys 6 assets and shorts 6 others with equal
money on each side, so its net weight is 0 and a market-wide move roughly cancels
(market-neutral).

The pair term is wᵢwⱼΣᵢⱼ, so the same pair can favour holding both on the same side or on
opposite sides:

- same side, positively correlated: risks add (penalty);
- opposite sides, positively correlated: risks cancel (reward, a hedge).

Three mutually correlated assets each want to be opposite the other two, which is
impossible. That is frustration. Galluccio, Bouchaud & Potters (1998 [abs]) show long/short
portfolios under a margin constraint reduce to spin-glass equations with couplings from the
inverse covariance, which has mixed signs even when all correlations are positive. They
find "the number of 'optimal' solutions is generically exponentially large" (about 10²⁹
for 100 US stocks) and that near-equal solutions can be far apart, which is the regime
QeMCMC needs. Long-only portfolios without a count constraint also show a spin-glass-like
landscape (Garnier-Brun 2021 [abs]).

Encoding: two bits per asset or separate long and short registers, each with its own XY
mixer so both counts stay fixed (Hodson 2019 [abs]). Moves are long↔unheld,
short↔unheld and long↔short. Sizes:

| Book | Valid portfolios |
|---|---|
| 2 long / 2 short of 12 | C(12,2) × C(10,2) = 2,970 |
| 3 long / 3 short of 16 | C(16,3) × C(13,3) = 160,160 |
| 6 long / 6 short of 16 | C(16,6) × C(10,6) = 1,681,680 |

Start at 2+2 of 12. 6+6 of 16 is too large for exact gaps and needs about 32 qubits.

### Rank 3: least-correlated k

Choosing k of 16 ETFs to maximize pairwise correlation distance is the Maximum Diversity
Problem. A 315-instance benchmark library and a comparison of 30 heuristics show plain local
search is not enough (Martí 2013; Wu & Hao 2013 [meta]). The related densest-k-subgraph
problem is hard to approximate (Manurangsi 2017 [meta]). Thresholding the correlation matrix
into a graph and asking for a k-independent set links to IBM's QeMCMC work on Maximum
Independent Set, which cites financial services as a motivation (Marshall 2026 [full]).

### Rank 4: credit-scoring feature selection

Choose k of n features to balance relevance to default against redundancy. Prior QUBO work:
1QBit on UCI German Credit (Milne 2017 [meta]), Mücke 2023 [abs], IBM (Zoufal 2023 [abs])
and American Express (Samanta 2025 [abs]). It has a natural sampling motive: a spread of
near-optimal feature sets supports stability checks and model averaging. Caveat (ours, from
how the papers describe the cost): the plain form rewards each feature and penalizes every
selected pair, so pair terms share one sign and frustration comes only from the count
constraint. Signed correlations or conditional mutual information add real sign mixing.

### What does not help

- Fixed transaction costs and turnover: linear in holdings, so they shift the optimum but
  add no frustration.
- Sector quotas: split the search graph without creating competing pair terms.
- Sharpe ratio and tracking a broad index: stay dominated by the market.
- Collateral, settlement and loan-pool selection: budgets and inequalities, not an exact
  count (Giron 2023; Braine 2021 [abs]).
- p-median and k-medoids have the strongest classical evidence of many swap optima
  (Hansen & Mladenović 1997; Alekseeva & Kochetov 2008 [meta]), but their objective takes a
  minimum over chosen sites, so it is not quadratic. Simulation only.

## 4. Tuning knobs

All knobs act through r or the sign pattern of the pair terms.

| Knob | Direction for more ruggedness | Finance reading |
|---|---|---|
| λ, or shrinking μ toward its average | Raise λ; shrink μ, down to μ = 0 | Distrust of mean estimates |
| Window length L | Shorter, so n/L approaches 1 | Noisy covariance gives random-sign noise modes (Laloux 1999 [abs]); Galluccio ties the number of optima to this noise |
| Covariance cleaning | Do not clean | Ledoit-Wolf shrinkage or random-matrix cleaning smooths the landscape |
| Universe | Add hedges (Treasuries, gold, USD, volatility) | Competing clusters of attractive and repulsive pairs |
| Position signs | Allow shorts | Pair effect flips with side |
| Factors per asset (planted family) | 1–3 at n = 16 | Wishart hardness peaks at few factors per asset (Hamze 2020 [abs]) |
| Temperature T | Near the barrier between the two best optima | Choose from the full gap-vs-T curve, not one value |

Adaptive instance search (mutate, keep what slows the solver) made spin-glass instances up
to about 250× harder than random ones (Marshall, Martín-Mayor & Hen 2016 [abs]). If we tune
λ, window or universe this way, every baseline must run on the same instances, or the set
is chosen against one method.

## 5. Metrics and the screen

At 4,368 states (and 2,970 for 2+2 of 12) every transition matrix fits in memory, so the
primary metric is exact:

- **Spectral gap** δ = 1 − max |λ| of the full transition matrix, swept over T. Relaxation
  time is 1/δ. Layden 2023 uses the same measure.

Three cheap landscape statistics should explain it:

1. Number of swap-local optima and the global optimum's basin share.
2. Barrier B: over all paths from the second-best optimum to the best, the smallest
   possible worst score drop along the path. A union-find sweep over states sorted by score
   gives it. Standard theory predicts 1/δ grows roughly like exp(B/T) at low T (ours, not
   checked on this problem).
3. Score gap and Hamming distance between the best two optima. QeMCMC needs a small gap and
   a large distance.

Autocorrelation length and fitness–distance correlation are weak here: a quadratic score on
the k-subset graph has very few independent components (Chicano, landscape theory [meta]).

**Screen, fixed before any QeMCMC run (heuristic):** keep instances with at least 3
swap-local optima and a global basin share below 30%, the bottom of di Tollo's range for
easy real instances. Report what fraction of windows pass.

For larger or hardware runs: TVD to the exact Boltzmann distribution (Arai & Kadowaki 2025
[abs]), autocorrelation decay (Kawamata 2026b [abs]), iterations to the global optimum
(Marshall 2026 [full]) and acceptance rate (Nakano 2024 [abs]). Log attempts, score
evaluations, shots and wall-clock time as separate fields.

## 6. Quantum proposal and baselines

**Proposal.** Evolve the current portfolio under the score Hamiltonian plus a complete-graph
XY mixer. XY and Z terms are real-symmetric, so the proposal is symmetric (Layden's
condition), keeps exactly k holdings, and moves several assets at once. Its classical
analogue is global swap. This follows from Layden's condition but is not published as a
QeMCMC result (ours). IBM's Maximum Independent Set work used a penalty and a plain X mixer
instead (Marshall 2026 [full]); here that would leave the valid set and waste proposals.

**Baselines,** all at the same target distribution, temperature and attempt budget:

| Baseline | Why |
|---|---|
| Local swap Metropolis | The current control |
| Uniform random k-subset | Layden's uniform baseline; reaches any portfolio in one step |
| Multi-swap and heat-bath swaps | Classical analogues of a non-local, score-informed proposal |
| Parallel tempering with swaps, budget summed over replicas | Standard method for rugged landscapes; most likely to erase a gain (Hukushima & Nemoto 1996) |
| Simulated annealing, tabu search, greedy restarts | Practical portfolio heuristics |
| Exact enumeration | Ground truth |
| Mismatched quantum proposal (wrong landscape) | Tests whether gains come from encoding the problem |
| Classically simulated quantum proposal | Tests whether any gain is quantum at all (Christmann 2025) |

Cluster moves (Swendsen-Wang, Wolff, Houdayer) are low priority: they gave almost no gap
improvement in Layden 2023 and do not keep the count fixed.

Sweep the mixer strength and evolution time; Layden's ranges were not optimized, and later
work found an optimal strength (Christmann 2025) and gains from adiabatic dressing
(Hsieh 2026). Present any n = 16 result as proposal efficiency at a fixed size, not a
scaling claim (Orfi & Sels 2024a).

## 7. Experiments

| ID | Experiment | Output |
|---|---|---|
| E0 | r, optima count, basin share, B and score gap for all 64 existing windows | Confirms r ≪ 1; half a day |
| E1 | Sweep r on the current 16 ETFs down to μ = 0; market-mode removal as ablation | Optima count, B, swap vs uniform δ(T) |
| E2 | E1 on the mixed-asset universe, window length L from about n to 4n | Fraction of windows passing the screen |
| E3 | Long/short, 2+2 of 12, then 3+3 of 16 | Same |
| E4 | Least-correlated k and k-independent set on the ETF correlation graph | Same |
| E5 | German Credit, 6 of 20, plain and signed couplings | Same |
| E6 | Exact XY-mixer QeMCMC transition matrices on instances that pass; sweep mixer strength, time and T | δ against every baseline in §6 |
| E7 | Scale the winning formulation to 6 of 20; then small hardware chains | Trend; acceptance rate and TVD on hardware |

## 8. What this does not support claiming

- That any finance problem is known to favour QeMCMC. None has been tested.
- That r ≈ 1 is a published threshold, or that B/T predicts δ on k-subset landscapes. Both
  are ours to test, and testing them is itself a contribution.
- That long/short with exact counts has exponentially many optima. Galluccio's count is for
  continuous weights.
- A speedup from any n = 16 result.
