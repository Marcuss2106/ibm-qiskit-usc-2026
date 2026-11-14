# References

Every entry was resolved in OpenAlex (W-id given). **Status**: J = peer-reviewed journal/
conference, P = preprint. **Read**: full = full text read for this synthesis; abs = abstract
read via OpenAlex; meta = metadata only (cited for its well-known standard content).
★ = one of the four papers in the study guide.

## QeMCMC

| Ref | Status | Read | DOI / ID | OpenAlex | Relevance |
|---|---|---|---|---|---|
| Layden, Mazzola, Mishmash, Motta et al. (2023). Quantum-enhanced Markov chain Monte Carlo. *Nature* 619, 282–287 | J | full (arXiv:2203.12497) | 10.1038/s41586-023-06095-4 | W4384009058 | Source of the roadmap's symmetric-proposal QeMCMC, α normalization, hardware Trotter scheme |
| ★ Marshall, Egger, Garn, Schiavello et al. (2026). Quantum-enhanced Markov Chain Monte Carlo for Combinatorial Optimization | P | full (v2 HTML) | 10.48550/arXiv.2602.06171 | W7128371520 | Optimization framing; warm start, filtering, parallel tempering; MIS to 117 qubits |
| Orfi & Sels (2024). Bounding the speedup of the quantum-enhanced Markov-chain Monte Carlo algorithm. *PRA* 110, 052414 | J | abs | 10.1103/PhysRevA.110.052414 | W4404281017 | No speedup for worst-case unstructured sampling |
| Hsieh, Orfi & Sels (2026). Adiabatic dressing of quantum-enhanced Markov chains. *PRA* | J | abs | 10.1103/x255-fw2l | W7147438972 | Delocalization vs acceptance trade-off |
| Nakano, Hakoshima, Mitarai, Fujii (2024). MCMC enhanced by a quantum alternating operator ansatz. *PRR* 6, 033105 | J | abs | 10.1103/PhysRevResearch.6.033105 | W4400977912 | Acceptance rate as a tunable proxy for spectral gap |
| Ferguson & Wallden (2025). QeMCMC for systems larger than a quantum computer. *PRR* 7, 013231 | J | abs | 10.1103/PhysRevResearch.7.013231 | W4408110273 | Coarse-graining; scaling beyond qubit count |
| Arai & Kadowaki (2025). Quantum annealing enhanced MCMC. *Sci. Rep.* | J | abs | 10.1038/s41598-025-07293-y | W4411872364 | Annealing-based proposals |
| Cao, Cui, Wang, Tang (2026). Irreversibility Enhances QeMCMC | P | abs | 10.48550/arXiv.2606.23350 | W7165683561 | Non-reversible variants |

## QAOA and constraint handling

| Ref | Status | Read | DOI / ID | OpenAlex | Relevance |
|---|---|---|---|---|---|
| Farhi, Goldstone, Gutmann (2014). A Quantum Approximate Optimization Algorithm | P | meta | 10.48550/arXiv.1411.4028 | W1568345435 | Original QAOA |
| Zhou, Wang, Choi, Pichler, Lukin (2020). QAOA: Performance, Mechanism, and Implementation on Near-Term Devices. *PRX* 10, 021067 | J | abs | 10.1103/PhysRevX.10.021067 | W2903058119 | Angle initialization heuristics, resources |
| ★ Giovagnoli (2025). An Introduction to the Quantum Approximate Optimization Algorithm | P | abs | 10.48550/arXiv.2511.18377 | W7106718748 | Tutorial; penalties; landscape symmetry/periodicity |
| Blekos et al. (2024). A review on QAOA and its variants. *Physics Reports* | J | meta | 10.1016/j.physrep.2024.03.002 | W4392877631 | Review of variants |
| Barkoutsos, Nannicini, Robert, Tavernelli, Woerner (2020). Improving Variational Quantum Optimization using CVaR. *Quantum* 4, 256 | J | abs | 10.22331/q-2020-04-20-256 | W2960556599 | CVaR objective |
| Hadfield, Wang, O'Gorman, Rieffel, Venturelli, Biswas (2019). From QAOA to a Quantum Alternating Operator Ansatz. *Algorithms* 12, 34 | J | meta | 10.3390/a12020034 | W2754868542 | Feasibility-preserving mixers |
| Wang, Rubin, Dominy, Rieffel (2020). XY mixers. *PRA* 101, 012320 | J | abs | 10.1103/PhysRevA.101.012320 | W2939513517 | XY mixers beat X mixer on constrained problems |
| Bärtschi & Eidenbenz (2019). Deterministic Preparation of Dicke States. *LNCS* (FCT 2019) | J | meta | 10.1007/978-3-030-25027-0_9 | W2937696121 | Feasible-subspace initial state |
| Bärtschi & Eidenbenz (2020). Grover Mixers for QAOA. *IEEE QCE* | J | abs | 10.1109/QCE49297.2020.00020 | W3029819693 | Applied to discrete portfolio rebalancing |
| Egger, Mareček, Woerner (2021). Warm-starting quantum optimization. *Quantum* 5, 479 | J | meta | 10.22331/q-2021-06-17-479 | W3088409280 | Warm starts (lineage of Marshall's warm start) |

## Portfolio optimization on quantum hardware

| Ref | Status | Read | DOI / ID | OpenAlex | Relevance |
|---|---|---|---|---|---|
| ★ Egger, Gambella, Mareček, McFaddin, Mevissen, Raymond, Simonetto, Woerner, Yndurain (2020). Quantum Computing for Finance: State-of-the-Art and Future Prospects. *IEEE TQE* | J | abs | 10.1109/TQE.2020.3030314 | W3037022125 | Application motivation |
| Herman et al. (2023). Quantum computing for finance. *Nat. Rev. Phys.* | J | meta | 10.1038/s42254-023-00603-1 | W4383879098 | Updated survey |
| Brandhofer, Braun, Dehn, Hellstern et al. (2022). Benchmarking the performance of portfolio optimization with QAOA. *Quantum Inf. Process.* | J | abs | 10.1007/s11128-022-03766-5 | W4313293044 | Closest QAOA analogue to our QUBO |
| Hodson, Ruck, Ong, Garvin, Dulman (2019). Portfolio rebalancing experiments using the Quantum Alternating Operator Ansatz | P | abs | 10.48550/arXiv.1911.05296 | W2989335074 | 8-stock analogue, hard-constraint mixers |
| Mancilla, Bouloumis, Goguikian (2026). Constrained Portfolio Optimization via QAOA with XY-Mixers and Trotterized Initialization | P | abs | 10.48550/arXiv.2602.14827 | W7129592122 | Dicke + XY QAOA with backtest |
| Lozano (2026). A Penalty-Free Pipeline for Direct Quantum-Annealer Portfolio Optimization | P | abs | 10.48550/arXiv.2605.17628 | W7160757885 | Evidence that cardinality penalties hurt hardware sampling |

## Encoding / benchmarking

| Ref | Status | Read | DOI / ID | OpenAlex | Relevance |
|---|---|---|---|---|---|
| Lucas (2014). Ising formulations of many NP problems. *Front. Phys.* 2, 5 | J | meta | 10.3389/fphy.2014.00005 | W2039122980 | Penalty/Ising encodings |
| Glover, Kochenberger, Du (2019). Quantum Bridge Analytics I. *4OR* 17 | J | meta | 10.1007/s10288-019-00424-y | W2990475267 | QUBO tutorial (expanded 2022: 10.1007/s10479-022-04634-2, W4226006885) |
| Kurebayashi, Yamashita, Tobe (2025). Optimization of Penalty Weights in Quantum Annealing. *APCC* | J | abs | 10.23919/APCC64555.2025.11279889 | W4417339407 | Penalty lower bounds |
| ★ Hellstern, Schacht, Zaefferer (2026). Comparing classical and quantum QUBO solvers | P | abs | 10.48550/arXiv.2610.35126 | W7223888756 | Fair-comparison methodology (code: 10.5281/zenodo.23661252) |
| Abbas et al. (2023). Quantum Optimization: Potential, Challenges, and the Path Forward (report) | Report | meta | 10.2172/2229681 | W4389750777 | Benchmarking practice |
| Metropolis, Rosenbluth, Rosenbluth, Teller, Teller (1953). *J. Chem. Phys.* 21, 1087 | J | meta | 10.1063/1.1699114 | W2056760934 | Metropolis rule |
| Hastings (1970). *Biometrika* 57, 97 | J | meta | 10.1093/biomet/57.1.97 | W2138309709 | MH with asymmetric proposals |
| Kirkpatrick, Gelatt, Vecchi (1983). Optimization by Simulated Annealing. *Science* 220 | J | meta | 10.1126/science.220.4598.671 | W2024060531 | Classical baseline |
| Earl & Deem (2005). Parallel tempering. *PCCP* 7 | J | meta | 10.1039/b509983h | W2170171286 | Classical baseline / Marshall extension |

## Finance methodology

| Ref | Status | Read | DOI / ID | OpenAlex | Relevance |
|---|---|---|---|---|---|
| Markowitz (1952). Portfolio Selection. *J. Finance* 7 | J | meta | 10.1111/j.1540-6261.1952.tb01525.x | W4232474910 | Mean–variance |
| Merton (1980). On estimating the expected return on the market. *JFE* 8 | J | meta | 10.1016/0304-405X(80)90007-0 | W3121451334 | μ estimation difficulty |
| Chopra & Ziemba (1993). The Effect of Errors in Means, Variances, and Covariances. *JPM* 19 | J | meta | 10.3905/jpm.1993.409440 | W2164883547 | μ errors dominate |
| Ledoit & Wolf (2004). Honey, I Shrunk the Sample Covariance Matrix. *JPM* 30 | J | meta | 10.3905/jpm.2004.110 | W3124027709 | Covariance shrinkage |
| DeMiguel, Garlappi, Uppal (2009). Optimal Versus Naive Diversification. *RFS* 22 | J | meta | 10.1093/rfs/hhm075 | W2163969674 | 1/N benchmark |
| Bailey & López de Prado (2014). The Deflated Sharpe Ratio. *JPM* 40 | J | meta | 10.3905/jpm.2014.40.5.094 | W3124863268 | Multiple-testing correction |
| Bailey, Borwein, López de Prado, Zhu (2016). The probability of backtest overfitting. *J. Comput. Finance* | J | meta | 10.21314/JCF.2016.322 | W2732395805 | Backtest overfitting |

## Software / data (from the roadmap)
- IBM Quantum / Qiskit QAOA tutorial — implementation workflow.
- yfinance — adjusted-close download.
