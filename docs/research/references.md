# References

Every entry was resolved in OpenAlex (W-id given).
**Status:** J = peer-reviewed journal or conference; P = preprint.
**Read:** full = full text read; abs = abstract read via OpenAlex; meta = metadata only,
cited for its well-known standard content.
★ = one of the four papers in the study guide.

## Quantum-enhanced MCMC

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| Layden, Mazzola, Mishmash, Motta et al. (2023). Quantum-enhanced Markov chain Monte Carlo. *Nature* 619, 282–287 | J | full | 10.1038/s41586-023-06095-4 | W4384009058 | The mechanism: symmetric circuit proposals plus Metropolis |
| ★ Marshall, Egger, Garn, Schiavello et al. (2026). Quantum-enhanced Markov Chain Monte Carlo for Combinatorial Optimization | P | full | 10.48550/arXiv.2602.06171 | W7128371520 | Optimization framing; iterations-to-optimum metric; hardware shot overhead |
| Kawamata, Nakano, Fujii (2026). Divide-and-conquer neural-network surrogates for quantum sampling: accelerating MCMC in large-scale constrained optimization. *Phys. Rev. Applied* | J | abs | 10.1103/qprn-rs96 | W7155415592 | **Closest prior work:** count-preserving XY proposals vs. Kawasaki dynamics |
| Kawamata & Fujii (2026). Hardware Demonstration of Neural-Surrogated QeMCMC for Large-Scale Constrained Boltzmann Sampling | P | abs | 10.48550/arXiv.2611.05883 | W7225323301 | Count-preserving QeMCMC on IBM Heron r2 |
| Orfi & Sels (2024). Bounding the speedup of the quantum-enhanced Markov-chain Monte Carlo algorithm. *PRA* 110, 052414 | J | abs | 10.1103/PhysRevA.110.052414 | W4404281017 | No worst-case speedup |
| Hsieh, Orfi & Sels (2026). Adiabatic dressing of quantum-enhanced Markov chains. *PRA* | J | abs | 10.1103/x255-fw2l | W7147438972 | Spread-vs-acceptance trade-off; motivates time sweep |
| Nakano, Hakoshima, Mitarai, Fujii (2024). MCMC enhanced by a quantum alternating operator ansatz. *PRR* 6, 033105 | J | abs | 10.1103/PhysRevResearch.6.033105 | W4400977912 | Symmetric QAOA-style proposals; acceptance rate as tuning signal |
| Shirai (2026). Quantum-echo Markov process for combinatorial optimization | P | abs | 10.48550/arXiv.2609.38943 | W7215077823 | Non-local vs. energy-local proposals; greedy descent helps |
| Ferguson & Wallden (2025). QeMCMC for systems larger than a quantum computer. *PRR* 7, 013231 | J | abs | 10.1103/PhysRevResearch.7.013231 | W4408110273 | Fewer qubits than variables |

## Count-preserving quantum circuits

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| Hadfield, Wang, O'Gorman, Rieffel, Venturelli, Biswas (2019). From QAOA to a Quantum Alternating Operator Ansatz. *Algorithms* 12, 34 | J | meta | 10.3390/a12020034 | W2754868542 | Feasibility-preserving mixers |
| Wang, Rubin, Dominy, Rieffel (2020). XY mixers: analytical and numerical results for the quantum alternating operator ansatz. *PRA* 101, 012320 | J | abs | 10.1103/PhysRevA.101.012320 | W2939513517 | XY mixers; ring and complete implementations |
| He, Shaydulin, Chakrabarti, Herman et al. (2023). Alignment between initial state and mixer improves QAOA performance for constrained optimization. *npj Quantum Inf.* | J | abs | 10.1038/s41534-023-00787-5 | W4389036166 | XY-mixer portfolio optimization on 32-qubit hardware |
| Mancilla, Bouloumis, Goguikian (2026). Constrained Portfolio Optimization via QAOA with XY-Mixers and Trotterized Initialization | P | abs | 10.48550/arXiv.2602.14827 | W7129592122 | XY mixer for cardinality-constrained portfolios |
| Brandhofer, Braun, Dehn, Hellstern et al. (2022). Benchmarking the performance of portfolio optimization with QAOA. *Quantum Inf. Process.* | J | abs | 10.1007/s11128-022-03766-5 | W4313293044 | Count-constrained portfolio QUBO; noise effects |
| Lozano (2026). A Penalty-Free Pipeline for Direct Quantum-Annealer Portfolio Optimization | P | abs | 10.48550/arXiv.2605.17628 | W7160757885 | Why count penalties fail on hardware |

## Classical search and MCMC

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| Kawasaki (1966). Diffusion Constants near the Critical Point for Time-Dependent Ising Models. I. *Phys. Rev.* 145, 224 | J | abs | 10.1103/PhysRev.145.224 | W1982789149 | Origin of the swap (spin-exchange) move |
| Chang, Meade, Beasley, Sharaiha (2000). Heuristics for cardinality constrained portfolio optimisation. *Comput. Oper. Res.* 27 | J | meta | 10.1016/S0305-0548(99)00074-X | W2151237529 | Classic heuristics benchmark for this problem |
| Crama & Schyns (2003). Simulated annealing for complex portfolio selection problems. *EJOR* 150 | J | meta | 10.1016/S0377-2217(02)00784-1 | W2113188547 | Swap-based simulated annealing for portfolios |
| Graham & Craven (2020). An exact algorithm for small-cardinality constrained portfolio optimisation. *JORS* | J | abs | 10.1080/01605682.2020.1718019 | W3003419766 | Local optima in cardinality-constrained portfolios. Note: continuous weights and an evolutionary algorithm's local optima, not equal weights under swaps, so not directly comparable to our §8.1 counts. |
| Metropolis, Rosenbluth, Rosenbluth, Teller, Teller (1953). *J. Chem. Phys.* 21, 1087 | J | meta | 10.1063/1.1699114 | W2056760934 | Acceptance rule |
| Hastings (1970). *Biometrika* 57, 97 | J | meta | 10.1093/biomet/57.1.97 | W2138309709 | Correction for asymmetric proposals |
| Kirkpatrick, Gelatt, Vecchi (1983). Optimization by Simulated Annealing. *Science* 220 | J | meta | 10.1126/science.220.4598.671 | W2024060531 | Annealing control |
| Earl & Deem (2005). Parallel tempering: theory, applications, and new perspectives. *PCCP* 7 | J | meta | 10.1039/b509983h | W2170171286 | Multi-temperature extension |

## Fair comparison

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| ★ Hellstern, Schacht, Zaefferer (2026). Comparing classical and quantum QUBO solvers: optimality, trajectory diagnostics, and limits of solver selection | P | abs | 10.48550/arXiv.2610.35126 | W7223888756 | Separate quality, certification and cost (code: 10.5281/zenodo.23661252) |
| Abbas, Ambainis, Augustino, Bärtschi et al. (2024). Challenges and opportunities in quantum optimization. *Nat. Rev. Phys.* | J | meta | 10.1038/s42254-024-00770-9 | W4403834027 | Benchmarking practice |

## Finance

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| Markowitz (1952). Portfolio Selection. *J. Finance* 7 | J | meta | 10.1111/j.1540-6261.1952.tb01525.x | W4232474910 | Mean–variance objective |
| Merton (1980). On estimating the expected return on the market. *JFE* 8 | J | meta | 10.1016/0304-405X(80)90007-0 | W3121451334 | Expected returns are hard to estimate |
| Chopra & Ziemba (1993). The Effect of Errors in Means, Variances, and Covariances on Optimal Portfolio Choice. *JPM* 19 | J | meta | 10.3905/jpm.1993.409440 | W2164883547 | Errors in means dominate |
| Ledoit & Wolf (2004). Honey, I Shrunk the Sample Covariance Matrix. *JPM* 30 | J | meta | 10.3905/jpm.2004.110 | W3124027709 | Covariance shrinkage option |
| ★ Egger, Gambella, Mareček, McFaddin et al. (2020). Quantum Computing for Finance: State-of-the-Art and Future Prospects. *IEEE TQE* | J | abs | 10.1109/TQE.2020.3030314 | W3037022125 | Application motivation |
| Herman, Googin, Liu, Sun et al. (2023). Quantum computing for finance. *Nat. Rev. Phys.* | J | meta | 10.1038/s42254-023-00603-1 | W4383879098 | Updated survey |

## Landscape structure (bead 5xy, added 2026-11-14)

Checks the §8.1 finding that real equal-weight mean–variance is near single-peaked under
swaps. Summary: the market-mode explanation is supported (Plerou 2002); Stopfer 2025
independently finds variance-minimizing portfolio problems harder for classical solvers
than return-maximizing ones; no paper found that reports single-peaked swap landscapes
for equal-weight selection; the M♮-concavity theorem does not apply (our real data
violate its exchange condition, see `experiments/landscape/exchange_test.py`).

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| Stopfer et al. (2025). Quantum Portfolio Optimization: An Extensive Benchmark | P | abs | 10.48550/arXiv.2509.17876 | W4415255583 | Closest benchmark: QA and QAOA vs MIP, SA, steepest descent, tabu, tailored heuristic on 270 real-stock instances. Variance-minimizing variant is harder for classical solvers than return-maximizing; MIP solves all instances optimally in seconds; tailored heuristic beats quantum. Supports our finding and our "no speedup" stance. |
| Plerou, Gopikrishnan, Rosenow, Amaral et al. (2002). Random matrix approach to cross correlations in financial data. *PRE* 65, 066126 | J | abs | 10.1103/PhysRevE.65.066126 | W1989576509 | Largest eigenvalue of stock correlations is "an influence common to all stocks" (the market mode); most other eigenvalues look random. Basis for our market-factor explanation and the dial (bead t3h). |
| Laloux, Cizeau, Bouchaud, Potters (1999). Noise Dressing of Financial Correlation Matrices. *PRL* 83, 1467 | J | abs | 10.1103/PhysRevLett.83.1467 | W2147675445 | Most of an empirical correlation matrix's eigenvalue spectrum matches random-matrix noise; caution on using sample covariance for risk. |
| Monge (2020). Equally weighted cardinality constrained portfolio selection via factor models. *Optim. Lett.* | J | meta | 10.1007/s11590-020-01571-6 | W2743014156 | Same problem class as ours (equal weight, choose k) solved via factor models. No abstract in OpenAlex; **read the full text next**: it may already describe the factor structure we found. |
| Ferrari, Fulci, Paterlini (2025). Selection Confidence Sets for Equally Weighted Portfolios | P | abs | 10.48550/arXiv.2510.14988 | W4415861724 | Optimal equal-weight subset is statistically uncertain; matches our small second-best gaps (near-ties). |
| Murota (2003). *Discrete Convex Analysis*. SIAM | J | meta | 10.1137/1.9780898718508 | W4206054140 | M♮-concave (valuated matroid) objectives: any single-exchange local optimum is global. Our data violate the condition, so it does not explain the finding. |
| Shioura & Tamura (2015). Gross substitutes condition and discrete concavity for multi-unit valuations: a survey. *J. Oper. Res. Soc. Japan* 58 | J | abs | 10.15807/jorsj.58.61 | W2099063943 | Links "gross substitutes" (economics) to M♮-concavity. |
| Murota & Shioura (2004). Quadratic M-convex and L-convex functions. *Adv. Appl. Math.* | J | meta | 10.1016/j.aam.2003.11.001 | W2016802101 | Conditions for a quadratic function to be M-convex; would characterize which covariance matrices give guaranteed single peaks. |

## Rugged landscapes

Added November 2026 for [`rugged-landscapes.md`](rugged-landscapes.md). OpenAlex IDs were
looked up by DOI; "—" means the lookup was not completed (OpenAlex daily limit reached).
Depth read reflects the research notes behind the page.

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| Galluccio, Bouchaud & Potters (1998). Rational decisions, random matrices and spin glasses. *Physica A* | J | abs | 10.1016/S0378-4371(98)00332-X | W2159940266 | Long/short portfolios as spin glasses; exponentially many far-apart optima |
| di Tollo (2015). Hybrid metaheuristic for portfolio selection: comparison with an exact solver and search space analysis. *FedCSIS* | J | full | 10.15439/2015f7 | W1925509017 | Only real-data local-optima count: 1–5 optima; hedged-pair instance is rugged |
| Hodson, Ruck, Ong, Garvin et al. (2019). Portfolio rebalancing experiments using the Quantum Alternating Operator Ansatz | P | abs | 10.48550/arXiv.1911.05296 | W2989335074 | Long/short encoding with separate XY mixers |
| Garnier-Brun, Benzaquen, Ciliberti & Bouchaud (2021). A new spin on optimal portfolios and ecological equilibria (title from memory; check arXiv) | P | abs | arXiv:2104.00668 | — | Many solutions even without shorts |
| Laloux, Cizeau, Bouchaud & Potters (1999). Noise dressing of financial correlation matrices. *PRL* 83, 1467 | J | abs | 10.1103/PhysRevLett.83.1467 | W2147675445 | Short windows add random-sign noise modes |
| Hamze, Raymond, Pattison, Biswas & Katzgraber (2020). Wishart planted ensemble: a tunably rugged pairwise Ising model. *PRE* 101, 052102 | J | abs | 10.1103/PhysRevE.101.052102 | W2947883854 | Planted factor-neutral family; easy–hard–easy |
| Hen, Job, Albash, Rønnow et al. (2015). Probing for quantum speedup in spin-glass problems with planted solutions. *PRA* 92, 042325 | J | meta | 10.1103/PhysRevA.92.042325 | W1636291537 | Frustrated-loop planting |
| Marshall, Martín-Mayor & Hen (2016). Practical engineering of hard spin-glass instances. *PRA* 94, 012320 | J | abs | 10.1103/PhysRevA.94.012320 | W2352629499 | Adaptive instance search; selection-bias warning |
| Li (2026). Structure leakage and verification hazards in planted-solution benchmarks. *IEEE Access* | J | meta | 10.1109/ACCESS.2026.3738535 | W7169510115 | Planted instances can leak structure |
| Orfi & Sels (2024b). Barriers to efficient mixing of quantum-enhanced Markov chains. *PRA* 110, 052434 | J | abs | 10.1103/PhysRevA.110.052434 | W4404692126 | Proposals must spread, but not fully thermalize |
| Christmann, Ivashkov, Chiurco & Mazzola (2025). From quantum-enhanced to quantum-inspired Monte Carlo. *PRA* 111, 042615 | J | abs | 10.1103/PhysRevA.111.042615 | W4409503533 | Classical emulation keeps part of the gain; optimal mixer strength |
| Arai & Kadowaki (2025). Quantum annealing enhanced Markov-chain Monte Carlo. *Sci. Rep.* | J | abs | 10.1038/s41598-025-07293-y | W4411872364 | TVD to Boltzmann as a metric |
| Hukushima & Nemoto (1996). Exchange Monte Carlo method and application to spin glass simulations. *JPSJ* 65, 1604 | J | meta | 10.1143/JPSJ.65.1604 | W2002664623 | Parallel tempering baseline |
| Ochoa & Veerapen (2018). Mapping the global structure of TSP fitness landscapes. *J. Heuristics* | J | abs | 10.1007/s10732-017-9334-0 | W2618079578 | Local optima networks and funnels |
| Martí, Gallego, Duarte & Pardo (2013). Heuristics and metaheuristics for the maximum diversity problem. *J. Heuristics* | J | meta | — | — | MDPLIB; 30 heuristics compared |
| Wu & Hao (2013). A hybrid metaheuristic method for the maximum diversity problem. *EJOR* | J | meta | — | — | Tabu with swap neighbourhoods |
| Manurangsi (2017). Almost-polynomial ratio ETH-hardness of approximating densest k-subgraph. *STOC* | J | meta | 10.1145/3055399.3055412 | W2552383377 | Least-correlated-k is hard |
| Hansen & Mladenović (1997). Variable neighborhood search for the p-median. *Location Science* | J | meta | 10.1016/S0966-8349(98)00030-8 | W1988423736 | Swap search stalls in p-median optima |
| Alekseeva & Kochetov (2008). Local search complexity for the p-median problem. *EJOR* 191(3) | J | meta | — | — | Tight PLS-complete swap search (title from RePEc listing, unverified) |
| Milne, Rounds & Goddard (2017). Optimal feature selection in credit scoring and classification using a quantum annealer. 1QBit white paper | P | meta | — | — | First credit feature-selection QUBO (German Credit) |
| Mücke, Heese, Müller, Wolter et al. (2023). Feature selection on quantum computers. *Quantum Mach. Intell.* | J | abs | 10.1007/s42484-023-00099-z | W4321610604 | k-of-n feature-selection QUBO |
| Zoufal, Mishmash, Sharma, Kumar et al. (2023). Variational quantum algorithm for unconstrained black box binary optimization: application to feature selection. *Quantum* 7, 909 | J | abs | 10.22331/q-2023-01-26-909 | W4229442489 | IBM feature selection |
| Samanta, Wang, Hodges, Ferenczi et al. (2025). Parametric quantum feature selection methods for fraud and default detection. *AAAI Symp. Ser.* | J | abs | 10.1609/aaaiss.v7i1.36910 | W7106481027 | American Express; banking use case |
| Giron, Korpas, Parvaiz, Malik et al. (2023). Approaching collateral optimization for NISQ and quantum-inspired computing. *IEEE TQE* 4 | J | abs | 10.1109/TQE.2023.3314839 | W4386699397 | Collateral: budget constraints, poor fit |
| Braine, Egger, Glick & Woerner (2021). Quantum algorithms for mixed binary optimization applied to transaction settlement. *IEEE TQE* | J | abs | 10.1109/TQE.2021.3063635 | W2979770774 | Settlement: inequality constraints, poor fit |

## Background (study guide)

| Reference | Status | Read | DOI / ID | OpenAlex | Why it matters |
|---|---|---|---|---|---|
| ★ Giovagnoli (2025). An Introduction to the Quantum Approximate Optimization Algorithm | P | abs | 10.48550/arXiv.2511.18377 | W7106718748 | QAOA tutorial: cost and mixer layers |
| Farhi, Goldstone, Gutmann (2014). A Quantum Approximate Optimization Algorithm | P | meta | 10.48550/arXiv.1411.4028 | W1568345435 | Original QAOA |

## Platform

- IBM Quantum Platform documentation, *Plans overview* and *Instances* guides (read
  November 2026): Open Plan allows "10 minutes of quantum processing unit (QPU) usage per
  28-day rolling window."
- yfinance: adjusted-close data download.
