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
| Graham & Craven (2020). An exact algorithm for small-cardinality constrained portfolio optimisation. *JORS* | J | abs | 10.1080/01605682.2020.1718019 | W3003419766 | Local optima in cardinality-constrained portfolios |
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
