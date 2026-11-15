# Rugged, cardinality-constrained portfolio formulations for QeMCMC benchmarking

Scope: discrete, exactly-k portfolio selection problems (binary x, Σx = k) whose landscapes under single swaps have many local optima. Project baseline for comparison: choose k = 5 of n = 16 ETFs, maximize S(x) = μ·x/k − λ·xᵀΣx/k². Every quarterly window had exactly one swap-local optimum. Cause: the common market factor makes most pairs positively correlated, and the linear (return) terms are about 13 times larger than the pairwise covariance terms.

Notation (plain Unicode): n assets, k held, μ mean returns, Σ covariance, C correlation, β market loadings, λ risk aversion, T number of return observations in the estimation window.

Source note: claims marked "background knowledge" were not checked against a fetched source in this session. The report writer should treat them as unverified or drop them.

---

## Q1. Why is standard Markowitz with cardinality easy on real equity data, and what does the OR literature say about its local-optima structure?

### Takeaway
The only direct landscape measurement found agrees with the project's result. On the OR-Library equity instances, a swap-type local search finds very few local minima (usually 1, at most 5) and one global minimum, with basins covering 30–60% of the search space (di Tollo 2015). Ruggedness appeared only in two cases: a different encoding, and a hand-built covariance with strongly negatively correlated asset pairs. The structural reason is that a dominant positive market factor makes the quadratic term nearly a function of one aggregate, β·x, so it adds almost no frustration.

### Cited Findings
- **Benchmark origin.** Chang, Meade, Beasley & Sharaiha, "Heuristics for cardinality constrained portfolio optimisation," Computers & Operations Research 27 (2000) 1271–1302, DOI 10.1016/s0305-0548(99)00074-x. This is the source of the OR-Library port1–port5 data sets (about 955 citations per OpenAlex). — [OpenAlex/DOI](https://doi.org/10.1016/s0305-0548(99)00074-x); [OR-Library portinfo](http://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html)
- **OR-Library file format.** Line 1 gives N. Each asset then has a line with its mean return and standard deviation, and each pair has a line "i j correlation". The unconstrained efficient frontiers are in portef1–5. — [OR-Library portinfo](http://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html)
- **OR-Library sizes and markets.** port1 Hang Seng, 31 assets. port2 DAX 100, 85 assets. port3 FTSE 100, 89 assets. port4 S&P 100, 98 assets. port5 Nikkei, 225 assets. All are single-country equity universes. — [di Tollo 2015, Table I (FedCSIS)](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **di Tollo 2015 setup.** "Hybrid Metaheuristic for Portfolio Selection: Comparison with an exact solver and search space analysis" (FedCSIS 2015, DOI 10.15439/2015f7). It uses a master–slave design: local search over the binary asset-selection vector with add / delete / replace (swap) moves, and a QP for the weights. It ran a deterministic steepest descent from many starts to count local minima on the OR-Library instances, at five return targets and several (kmin, kmax) settings. — [di Tollo 2015](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **di Tollo 2015, results on real data.** For OR-Library instance 4 (S&P 100), Table V shows 1 minimum in most cells, with a maximum of 5 (at kmin = 1, kmax = 6 and at kmin = kmax = 3). Quote: "instances at hand show a small number of local minima and only one global minimum. This clearly indicates a situation in which the search landscape is rather smooth." Global-minimum basins cover 30% to 60% of the search space. — [di Tollo 2015](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **di Tollo 2015 on the general pattern.** Quote: "preliminary analysis have suggested us that this is a common feature in financial market related instances … but makes impossible to test the robustness of our approach." — [di Tollo 2015](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **di Tollo 2015, effect of encoding.** A weights-only ("monolithic") formulation with threshold accepting, where moves shift weight between assets, made "the number of local minima … dramatically higher" with "tiny" basins. The certified optimum was not found. Ruggedness therefore depends on the move set and encoding as well as on the data. — [di Tollo 2015](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **Murray & Shek (Stanford CME334 slides, 2012).** Adding a cardinality constraint turns the convex QP into a non-convex mixed-integer problem whose feasible region can have many local optima. This is a general statement, not a measured count. — [Murray & Shek 2012](https://web.stanford.edu/class/cme334/docs/2012-10-22-murray_shek_portfolio.pdf) (via search summary; the PDF was not fetched)
- **Other heuristic studies.** Schaerf's tabu search for constrained portfolios combines several neighborhood relations and is tested on public benchmarks. These papers report solution quality, not landscape statistics. — [Schaerf, arXiv cs/0104017](https://arxiv.org/abs/cs/0104017)
- **Index tracking (Beasley, Meade & Chang 2003).** "An evolutionary heuristic for the index tracking problem," EJOR 148(3) 621–643, DOI 10.1016/S0377-2217(02)00425-3. It covers cardinality-limited index tracking with transaction costs on five public data sets from major world markets. No local-optima counts were found. — [EconPapers](https://econpapers.repec.org/RePEc:eee:ejores:v:148:y:2003:i:3:p:621-643); [Beasley tracking page](https://people.brunel.ac.uk/~mastjjb/jeb/track.html)

### Inferences
- **Mechanism (our analysis, consistent with di Tollo's data).** Take a one-factor model, Σ = σm²·ββᵀ + D, with D diagonal. With equal weights, the quadratic term becomes σm²·(β·x)² plus a separable term. So the score is "separable linear part − λ·g(β·x)" with g convex in a single scalar. A convex function of one aggregate adds no frustration. Each asset's marginal value changes almost uniformly as the aggregate rises, so swaps behave like sorting by an adjusted score, and essentially one local optimum results. A strong μ term (13 times the pair terms in our data) makes this even more true.
- **Where ruggedness needs to come from.** It needs pairwise couplings that are (a) not close to rank one, (b) mixed in sign, so that pairs which are good together are bad with others, and (c) at least comparable in size to the spread of the linear terms. The project should report a diagnostic per window: the ratio of the spread of linear terms to the spread of pairwise terms, plus the fraction of negative off-diagonal entries in the coupling matrix after the market factor is removed.
- **Benchmark scale.** OR-Library instances are larger (n = 31–225) than our simulation budget. To use them, take a sub-universe of 16–20 assets. di Tollo's evidence suggests they will still be smooth.

### Gaps
- No access to the Chang et al. 2000 full text, so whether it reports anything about local optima is unknown.
- No landscape statistics were found for Woodside-Oriakhi, Lucas & Beasley (2011, EJOR) or Cesarone, Scozzari & Tardella (2013, Annals of OR / Computational Management Science). These are known heuristic and exact-method comparisons (background knowledge). Neither paper was fetched.
- The known result that low-rank covariance makes cardinality QPs easy (polynomial for fixed rank) is background knowledge only. No citation was verified.

---

## Q2. Which modifications create ruggedness? (Assessment of each option against the project's needs)

### Takeaway
The best-supported route to frustration is to let pairwise terms with mixed signs dominate. Three ways to do it: (1) work in residual, market-removed covariance with μ shrunk or set to zero; (2) mix asset classes so some correlations are negative; (3) allow long/short signs. Option 3 is the one with the strongest theory: Galluccio–Bouchaud–Potters show exponentially many optima, driven by the inverse covariance. A useful finance-to-spin-glass bridge is the Wishart planted ensemble: minimizing ‖Wᵀs‖² over ±1 positions is the variance of a long/short book estimated from M = αN return samples. It is frustrated and hardest at intermediate α, and turns ferromagnetic (easy) as α grows. Linear add-ons such as fixed transaction costs or turnover do not create ruggedness by themselves.

### Cited Findings
- **Galluccio, Bouchaud & Potters 1998**, "Rational decisions, random matrices and spin glasses," Physica A, DOI 10.1016/s0378-4371(98)00332-x.
  - Setting: futures or margin accounts with long and short positions, under the nonlinear constraint Σ γ·Wᵢ·|pᵢ| = W. Quote: "it is the nonlinear form of the above constraint that makes the problem interesting."
  - The optimality conditions reduce to Sᵢ = sign(Hᵢ + Σⱼ Jᵢⱼ Sⱼ), with spins Sᵢ = sign(pᵢ) and couplings J = μ·C⁻¹ (the inverse covariance). These are the TAP equations for metastable spin-glass states. Minimum risk R = μ²·Σ Sⱼ C⁻¹ⱼₖ Sₖ.
  - Quote: "the number of 'optimal' solutions is generically exponentially large." For US stocks, "an optimal portfolio with 100 assets can be composed in ∼10²⁹ different ways." Exact enumeration was run up to N = 27.
  - Quasi-degenerate solutions "can be very far from each other."
  - — [arXiv cond-mat/9801209](https://arxiv.org/abs/cond-mat/9801209); [DOI](https://doi.org/10.1016/s0378-4371(98)00332-x)
- **Hamze, Raymond, Pattison, Biswas & Katzgraber**, "The Wishart planted ensemble: A tunably-rugged pairwise Ising model with a first-order phase transition," Phys. Rev. E 101, 052102 (2020), arXiv 1906.00275.
  - Construction: W is N×M with M = αN columns orthogonal to a planted state t. The energy is G(s) = ½·sᵀWWᵀs = ½‖Wᵀs‖², and the couplings are J = −(1/N)·WWᵀ with the diagonal zeroed.
  - Large M gives a "Curie-Weiss ferromagnet, whose ground state is easy to find due to the lack of frustration." Hardness shows a "pronounced easy-hard-easy profile," with peak solution time "many orders of magnitude" above the easy regimes.
  - For α < 1, a locally stable paramagnetic state "correlates strongly with difficulty."
  - — [arXiv 1906.00275](https://arxiv.org/abs/1906.00275)
- **Chook suite.** Implements the Wishart planted ensemble, with α = M/N as the hardness knob. VeloxQ reports hard-regime Wishart instances defeating all tested solvers even at N = 100. — [Chook arXiv 2005.14344](https://arxiv.org/pdf/2005.14344); [VeloxQ arXiv 2501.19221](https://arxiv.org/pdf/2501.19221) (both via search summary, not fetched)
- **di Tollo 2015, rugged artificial instance.** All rᵢ = 1. The covariance is block-diagonal: a perfectly anti-correlated first pair (off-diagonal −1), then pairs with off-diagonal −0.9, and no cross-block correlation.
  - The best portfolio holds only the first pair. Every pair (i, i+1) of odd/even assets is a local optimum, because breaking a hedged pair raises risk. The global optimum's relative basin shrinks as 1/n.
  - Quote: "such an instance could be hardly found over real markets, even its presence is not forbidden by structural properties."
  - "no matter the neighborhood size, it is always possible to devise artificial instances whose minima are composed by subsets that have to be moved jointly."
  - — [di Tollo 2015](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **Hodson, Ruck, Ong et al. 2019**, "Portfolio rebalancing experiments using the Quantum Alternating Operator Ansatz," arXiv 1911.05296.
  - Ternary positions zᵢ ∈ {−1, 0, +1} (short / none / long), encoded with two bits per asset.
  - Cost: λ·Σσᵢⱼzᵢzⱼ − (1−λ)·Σμᵢzᵢ, plus a fixed trading cost T for each changed position relative to the previous holdings y. Net lots Σzᵢ = D = 4.
  - Data: 8 ASX stocks from 2017 daily returns (AMP, ANZ, BHP, BXB, CBA, CSL, IAG, MQG), giving 1,820 feasible of 65,536 states.
  - With long/short, the ±σᵢⱼ couplings change sign with the position, so a positively correlated universe still creates mixed-sign effective couplings.
  - — [arXiv 1911.05296 (HTML)](https://arxiv.org/html/1911.05296)
- **Lobo, Fazel & Boyd 2006**, "Portfolio optimization with linear and fixed transaction costs," Annals of OR, DOI 10.1007/s10479-006-0145-1. Fixed costs make the problem non-convex and are handled by convex relaxation and heuristics. — [DOI](https://doi.org/10.1007/s10479-006-0145-1) (metadata only)
- **Shinzato & Yasuda 2015.** Belief propagation for portfolio optimization (statistical-mechanics line of work). **Ciliberti, Kondor & Mézard 2007** study the feasibility of expected-shortfall (CVaR) optimization. Both are relevant to the CVaR option but were not read. — [Shinzato & Yasuda DOI](https://doi.org/10.1371/journal.pone.0134968); [Ciliberti, Kondor & Mézard DOI](https://doi.org/10.1201/9781420081923.ch14)

### Inferences: option-by-option assessment for "exactly k of n, swap moves, pairwise/higher terms dominate and are frustrated"

| Option | Creates frustration? | Why / caveat | Verdict |
|---|---|---|---|
| Long/short or market-neutral (ternary z, or fixed counts of k_L longs and k_S shorts) | Yes, strongly | The effective coupling between positions i and j is σᵢⱼ·zᵢzⱼ. Pairing a long with a short flips the sign, so "hedge pairs" compete. Galluccio et al. show exponentially many optima driven by C⁻¹ (mixed sign even when C is all positive). | **Top choice.** Use two exact-count registers (k_L of n long, k_S of n short, no overlap), or k held plus a sign bit. Fits XY mixers per register, as in Hodson et al.'s hard-constraint mixers. |
| Residual (factor-removed) covariance, μ shrunk to zero or small | Yes | Removing the market mode leaves residual correlations of both signs, near zero on average. The rank-one "ferromagnetic" part is gone, so pair terms set the landscape. | **Top choice and the easiest change.** Regress each ETF on SPY (or remove the first principal component). Set Σ_res = Σ − σm²·ββᵀ. Use μ = 0 or a heavily shrunk μ, or raise λ until pairwise spread exceeds linear spread. |
| Short estimation windows (T close to n) | Plausibly | A sample covariance from few observations is "Wishart-like". In the Wishart planted ensemble, minimizing ‖Wᵀs‖² over ±1 is hardest at intermediate α = M/N and easy at large α, which corresponds to long windows. | **Good knob.** Sweep T (for example 20–60 daily returns at n = 16) and measure the number of local optima. Caveat: the market factor still dominates unless returns are residualized or positions are signed. |
| Mixed asset classes (equity, Treasuries, gold, commodities, USD, volatility) | Partly | Negative stock–bond and equity–VIX correlations add pairs with negative coupling. These are hedging pairs, similar in shape to di Tollo's artificial instance. The sign of the stock–bond correlation depends on the regime (background knowledge: negative in roughly 2000–2021, positive in 2022). | **Good, needs a check per window.** Count windows with ≥ 2 local optima. Expect variation from window to window. |
| Sector or group constraints (exactly kg per group) | Weak | These split the swap graph and restrict moves, but add no frustrated couplings. Within groups the market factor still dominates. | Low value for ruggedness. Can add disconnected-looking basins if swaps across groups are forbidden. |
| Minimum buy-in thresholds or round lots | Not with equal weights | These matter only with continuous or integer weights. Under the project's equal-weight scheme they disappear. | Skip. |
| Fixed transaction costs or turnover from an existing portfolio | No (linear) | With binary holdings, the cost for each change is linear in x. It moves the optimum toward the current holdings but adds no frustration. It does make the landscape time-dependent. | Use only as an add-on to a frustrated core. |
| Diversification ratio, maximum diversification, risk parity | Higher-order and non-quadratic | The diversification ratio (σ·x)/sqrt(xᵀΣx) is a ratio, which equal-weight swaps do not handle well. Multimodality was not established. | Optional. The classical MCMC and a statevector-diagonal phase can evaluate any score, but a hardware phase would need a Taylor or QUBO approximation. |
| Sharpe ratio (μ·x)/sqrt(xᵀΣx) | Mild | Fractional and quasi-convex. With a dominant market factor it is still close to sorting. | Low priority. |
| CVaR or VaR from scenarios | Possibly | Max over scenarios and tail averages give piecewise, higher-order structure. Barkoutsos's "CVaR" is a different thing: an aggregation of measurement samples in variational algorithms, not a portfolio risk measure. | Medium. Needs scenarios and is not quadratic. |
| Higher moments (coskewness, cokurtosis) | Yes in principle | Cubic and quartic coskewness terms take mixed signs. Estimation noise is large for small T. | Medium. Simulation only (many-body phases). |
| Index tracking / enhanced indexing (min (x/k − b)ᵀΣ(x/k − b)) | Weak with a broad market index | The linear term −2bᵀΣx/k is market-factor dominated, so the problem behaves like the baseline. | Low, unless the tracked target is a long/short factor portfolio. |
| Pairs or statistical-arbitrage basket selection | Yes, by construction | Pairs with strong co-movement act as "must-move-together" units, which is exactly di Tollo's hard pattern. | Good as a planted / semi-synthetic generator. |

- **Recommended concrete formulation A: residual mean-variance.** Choose 5 of 16 ETFs to minimize xᵀΣ_res·x/k² − η·μ_res·x/k. Use small η so that the linear spread is ≤ the pairwise spread.
- **Recommended concrete formulation B: market-neutral long/short with exact counts.** Hold k_L = 3 longs and k_S = 3 shorts from n = 16, with long and short sets disjoint and weights ±1/k. Minimize the variance of the signed portfolio minus η times its expected return.
  - The search space is C(16,3)·C(13,3) = 560·286 = 160,160 states, which can still be enumerated.
  - At n = 12 with k_L = k_S = 2: C(12,2)·C(10,2) = 66·45 = 2,970 states.
  - Swap moves become long-swap, short-swap, and long↔short sign flips.
- **Recommended concrete formulation C: semi-synthetic planted.** Build Σ from W·Wᵀ, with W made of T ≈ αn residualized return vectors (a real-data Wishart). Optionally orthogonalize to a planted k-subset. This is a direct finance analogue of the Wishart planted ensemble, with a tunable hardness knob.

### Gaps
- No published fitness-landscape study was found that counts swap local optima for long/short, residual, or mixed-asset cardinality portfolios. The table above is our reasoning and must be validated with `qemcmc.landscape`.
- Galluccio et al. count stationary (TAP) solutions without a cardinality constraint. Their exponential count is not proven to carry over to exactly-k swap neighborhoods.
- Wishart-ensemble hardness results are for ±1 spins with no field and no cardinality constraint. The mapping to exactly-k 0/1 selection is our inference.

---

## Q3. Evidence of multi-modality (papers counting local optima or showing heuristics trapped)

### Takeaway
Direct counts are rare. di Tollo (2015) is the clearest. It finds 1–5 minima on real OR-Library data and many minima on an anti-correlated, pair-structured artificial instance, where steepest and first descent got trapped depending on the starting point while tabu search escaped. Galluccio et al. (1998) give an analytic count that is exponential in N for long/short margin portfolios. The landscape-analysis literature on portfolio problems is otherwise thin.

### Cited Findings
- **di Tollo 2015, local minima counts.** Table V (OR-Library instance 4) reports local-minima counts of 1–5 across cardinality and return settings. On the artificial instance, "SD and FD performances are greatly affected by the starting solution (and anyhow much poorer than TS+QP)." — [di Tollo 2015](https://annals-csis.org/Volume_5/pliks/7.pdf)
- **Galluccio et al., exponential count.** The number of optimal portfolios grows exponentially in N. Exact enumeration up to N = 27 matches the theory, with an exponent f(a) of about 0.84·a^(1/4) for small a. — [arXiv cond-mat/9801209](https://arxiv.org/abs/cond-mat/9801209)
- **Tagawa & Orito 2023.** "Fitness Landscape Analysis of Prospect Theory-Based Portfolio Optimization Problem Using Loan" (SICE 2023, DOI 10.23919/sice59929.2023.10354104). A landscape-analysis paper on a nonconvex (prospect-theory) portfolio objective. It was not read. — [DOI](https://doi.org/10.23919/sice59929.2023.10354104)
- **Galluccio et al., distance between solutions.** Quasi-degenerate optimal portfolios are far apart ("it can be rational to follow two totally different strategies"). Large Hamming distance between near-optimal solutions is the regime where non-local proposals such as QeMCMC could help. — [arXiv cond-mat/9801209](https://arxiv.org/abs/cond-mat/9801209)

### Inferences
- The project's finding (one optimum per window) is consistent with the only real-data landscape count found. This strengthens the case for reporting it as an expected result rather than a bug.
- di Tollo's artificial matrix gives a ready-made small benchmark with a known answer. For n = 16 there are 8 anti-correlated pairs. Generalize it to exactly-k by choosing k = 4 (two pairs) or adding block triples, with a known global optimum and a basin that shrinks as 1/n.

### Gaps
- The Tagawa & Orito paper and Maringer's book (Portfolio Management with Heuristic Optimization, 2005) may contain landscape statistics but were not accessed.
- No study measuring fitness–distance correlation or autocorrelation length for cardinality portfolios was located.

---

## Q4. Quantum finance cardinality-constrained QUBO papers: what data, and any hard or rugged instances?

### Takeaway
The quantum portfolio papers checked used small real equity sets: 8 ASX stocks (Hodson), DAX 30 (Brandhofer), and other bank data sets. None reported a landscape analysis or deliberately rugged instances. Brandhofer et al. define an easy/hard criterion, but it concerns QAOA performance, not local-optima structure. Hodson's ternary long/short encoding with Hamming-weight (parity-band) XY mixers is the most directly reusable design for a frustrated, count-preserving variant.

### Cited Findings
- **Hodson et al. 2019.** Eight ASX20 stocks, daily 2017 returns (252 days), annualized by ×250, plus monthly windows for six rebalances.
  - Uses parity-ring XY mixers on the long and short registers.
  - Local optima and approximation ratio were not analyzed, and no hard instances were identified. Unscaled daily μ and Σ made the cost too small for γ to matter.
  - — [arXiv 1911.05296](https://arxiv.org/html/1911.05296)
- **Brandhofer et al. 2022/2023**, "Benchmarking the performance of portfolio optimization with QAOA," Quantum Information Processing 22, 25. Cardinality-constrained QUBO. The ancillary files are named DAX30_Daily_Covar_5y.csv and DAX30_Daily_Returns_5y.csv, so the data are likely DAX 30, five years of daily data. The paper defines a criterion that separates "easy" from "hard" instances. — [arXiv 2207.10555](https://arxiv.org/abs/2207.10555)
- **Barkoutsos et al. 2020**, "Improving Variational Quantum Optimization using CVaR," Quantum 4, 256, DOI 10.22331/q-2020-04-20-256. Here CVaR aggregates sampled energies, rather than serving as a portfolio risk measure. — [DOI](https://doi.org/10.22331/q-2020-04-20-256)
- **Mugel et al. 2022**, "Dynamic portfolio optimization with real datasets using quantum processors and quantum-inspired tensor networks," Phys. Rev. Research 4, 013006, DOI 10.1103/physrevresearch.4.013006. — [DOI](https://doi.org/10.1103/physrevresearch.4.013006) (data details not fetched)
- **Herman et al. 2023**, "Quantum computing for finance," Nature Reviews Physics, DOI 10.1038/s42254-023-00603-1, with the earlier arXiv survey 2201.02773. — [DOI](https://doi.org/10.1038/s42254-023-00603-1)
- **Rosenberg et al. 2015/2016**, "Solving the optimal trading trajectory problem using a quantum annealer," IEEE JSTSP, DOI 10.1109/jstsp.2016.2574703. — [DOI](https://doi.org/10.1109/jstsp.2016.2574703)
- **Mixer papers.**
  - The Grover-mixer QAOA paper (arXiv 2006.00354) describes discrete portfolio rebalancing in "bands" defined by the Hamming weight of the short register. Separate XY-ring mixers on the long and short registers stop mixing between bands. — [arXiv 2006.00354](https://arxiv.org/pdf/2006.00354)
  - A 2023 study finds that aligning the initial state with the mixer improves constrained portfolio QAOA. It ran a 32-qubit ring-XY experiment on a trapped-ion device. — [arXiv 2305.03857](https://arxiv.org/pdf/2305.03857)
- **QeMCMC.**
  - Layden et al. 2023, "Quantum-enhanced Markov chain Monte Carlo," Nature, DOI 10.1038/s41586-023-06095-4. — [DOI](https://doi.org/10.1038/s41586-023-06095-4)
  - Orfi & Sels 2024 bound the speedup, DOI 10.1103/physreva.110.052414. — [DOI](https://doi.org/10.1103/physreva.110.052414)
  - Marshall, Egger et al. 2026, QeMCMC for combinatorial optimization, arXiv 2602.06171. — [DOI](https://doi.org/10.48550/arxiv.2602.06171)
  - These papers and the Layden benchmarks used spin-glass (Sherrington–Kirkpatrick-type) instances, not portfolios. That matters here: QeMCMC's reported advantage is on frustrated landscapes. (Background knowledge for Layden's instance class.)

### Inferences
- Because the quantum portfolio literature uses market-factor-dominated equity data and reports no ruggedness, a team that introduces a frustrated, exactly-k finance instance would be filling a real gap. Frame it as "making the finance instance resemble the spin-glass regime where QeMCMC was shown to help."
- Hodson's encoding (two exact-count registers with XY mixers, plus fixed costs measured from the previous holdings) maps directly to formulation B above.

### Gaps
- The exact contents of the Brandhofer data, the hard/easy criterion, the Mugel data set, and the survey's comments on instance hardness were not verified.
- No quantum portfolio paper reporting local-optima counts was found.

---

## Q5. Practical small data sets: which give mixed-sign correlations?

### Takeaway
Single-country equity sets (OR-Library port1–5, ASX, DAX 30) will reproduce the "one optimum" result. Mixed-sign structure comes from mixed asset-class ETF universes, residualized returns, long/short signs, or short windows. A concrete recipe: 16 liquid ETFs across equities, Treasuries, credit, gold, commodities, USD and volatility, residualized on SPY, with a quarterly-window sweep and a check per window.

### Cited Findings
- OR-Library port1–5 are single-index equity universes of 31–225 stocks. — [di Tollo 2015 Table I](https://annals-csis.org/Volume_5/pliks/7.pdf); [OR-Library](http://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html)
- Hodson used 8 ASX20 stocks (2017). Brandhofer appears to have used DAX 30. — [Hodson](https://arxiv.org/html/1911.05296); [Brandhofer](https://arxiv.org/abs/2207.10555)
- Large-N financial correlation matrices are dominated by a market mode, with most other eigenvalues inside the random-matrix noise band. Plerou et al., "Random matrix approach to cross correlations in financial data," Phys. Rev. E 65, 066126 (2002). — [DOI](https://doi.org/10.1103/physreve.65.066126) (background knowledge of content; metadata confirmed via OpenAlex)

### Inferences: data recipes (n ≈ 12–20, k ≈ 3–8)
1. **Mixed-asset ETF universe (n = 16).** Use SPY, EFA, EEM, IWM, TLT, IEF, SHY, TIP, LQD, HYG, GLD, SLV, DBC (or USO), UUP, VIXY (or VXX, shorter history), and VNQ. Equity–Treasury, equity–USD and equity–VIX pairs are expected to be negative in many windows. Check this per window rather than assuming it.
2. **Residualize.** Regress daily returns on SPY (or remove the first principal component) and use the residual covariance. Set μ to zero or shrink it heavily. Raise λ, or report the ratio of linear spread to pairwise spread and target values ≤ 1.
3. **Long/short variant on the same data.** Use k_L = k_S = 3 (or 2 at n = 12), or a sign bit per held asset. Even all-positive correlations give mixed effective couplings.
4. **Window-length sweep.** Use T from about n to about 4n daily observations. Shorter windows make sample couplings noisier and more "Wishart" (the hard regime at intermediate α). This adds estimation noise, which is fine for a benchmark of optimization difficulty.
5. **Planted control.** Use di Tollo's block covariance (−1 and −0.9 hedge pairs, equal μ), or a Wishart-planted Σ = WWᵀ built from residual returns. Either gives a known optimum and tunable ruggedness.
6. **Other public sources (not verified here).** Kenneth French's industry or size–value portfolios are long-only and market-dominated, so residualize them. Crypto is highly co-moving, with a strong market mode, so it is unlikely to help unless residualized.
7. **Acceptance test before running QeMCMC.** For each window, use `qemcmc.landscape` to count swap local optima, the global optimum's basin share, and the Hamming distance between the best two local optima. Keep windows or instances with ≥ 3 local optima and a global basin share < 30%. The 30% figure comes from the bottom of di Tollo's range for easy real instances.

### Gaps
- The correlation signs for the ETF list were not computed in this session. The stock–bond sign flip in 2022 is background knowledge and should be verified on the project's own data.
- No reference fixes a threshold for "enough local optima" for MCMC benchmarking. The 30% basin threshold is a heuristic.
