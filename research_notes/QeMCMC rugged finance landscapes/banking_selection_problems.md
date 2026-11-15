# Banking and non-portfolio finance selection problems as QeMCMC candidates (k-of-n, rugged, multi-peaked)

Scope note: this covers discrete, cardinality-constrained finance and banking problems other than plain mean-variance portfolio selection. The research used OpenAlex for metadata (titles, authors, years, DOIs) plus web fetches of abstracts. Many full texts (Springer, IEEE) were paywalled. So exact coefficient signs are often stated from the problem structure rather than read off the paper, and the notes flag where that is the case. The date is November 2026, and several 2026 arXiv items appear in OpenAlex.

Notation used below (plain Unicode). The decision vector is x ∈ {0,1}^n with Σ x_i = k, and the energy is E(x) = Σ h_i x_i + Σ_{i<j} J_ij x_i x_j (+ higher order). A "repulsive" coupling means J_ij > 0 under minimization, which penalizes selecting i and j together. An "attractive" coupling means J_ij < 0.

## Key question 1: Catalog of candidate use cases (formulation, why k-of-n, ruggedness evidence, prior QUBO work, public data)

### Takeaway
The best-documented non-portfolio finance QUBO is credit-scoring feature selection with a fixed number of features: 1QBit 2017, Mücke et al. 2023, Zoufal et al. 2023 (IBM), and American Express 2025. It is quadratic, k-of-n, built on the public German Credit data, and its importance-versus-redundancy structure maps onto the maximum-diversity / densest-k-subgraph family, which the operations research literature treats as needing metaheuristics. Facility location (p-median, branch/ATM siting) and k-medoids scenario or ensemble selection have the strongest classical evidence of many local optima under swap moves. However, they are not natively quadratic: their min-over-sites objective is higher-order, or needs auxiliary assignment qubits.

### Cited Findings

**A. Credit-scoring / default-prediction feature selection (k of n features)**
- Milne, Rounds and Goddard (1QBit, 2017 whitepaper), "Optimal Feature Selection in Credit Scoring and Classification Using a Quantum Annealer". It casts feature selection as a QUBO whose cost function balances each feature's influence on the credit outcome against the features' independence from one another, weighted by a parameter α. It was tested on the UCI German Credit Data, and against recursive feature elimination it gave a smaller subset without losing accuracy. — [1QBit whitepaper](https://1qbit.com/whitepaper/optimal-feature-selection-in-credit-scoring-classification-using-quantum-annealer/); described as a proof of principle on the 1QBit SDK in [Orús, Mugel, Lizaso 2019 review (arXiv 1807.03890)](https://arxiv.org/pdf/1807.03890)
- Orús, Mugel, Lizaso, "Quantum computing for finance: Overview and prospects", Reviews in Physics (2019), DOI 10.1016/j.revip.2019.100028, about 790 citations in OpenAlex. — [OpenAlex/DOI](https://doi.org/10.1016/j.revip.2019.100028)
- Mücke, Heese, Müller, Wolter, Piatkowski, "Feature selection on quantum computers", Quantum Machine Intelligence (2023), DOI 10.1007/s42484-023-00099-z. It is a QUBO that "allows to select a specified number of features based on their importance and redundancy", evaluated on a classical computer, a gate-based quantum computer and a quantum annealer. — [arXiv 2203.13261](https://arxiv.org/abs/2203.13261); [DOI](https://doi.org/10.1007/s42484-023-00099-z)
- Zoufal, Mishmash, Sharma, Kumar et al. (IBM), "Variational quantum algorithm for unconstrained black box binary optimization: Application to feature selection", Quantum 7, 909 (2023), DOI 10.22331/q-2023-01-26-909. This is VarQFS, and later work describes it as tested on credit-risk data. The objective there is a black-box model loss, which is non-quadratic (effectively all orders). — [Quantum journal](https://quantum-journal.org/papers/q-2023-01-26-909/); [DOI](https://doi.org/10.22331/q-2023-01-26-909)
- Samanta, Wang, Hodges, Ferenczi et al. (American Express), "Parametric Quantum Feature Selection Methods for Fraud and Default Detection", AAAI Symposium Series 7(1) (2025), DOI 10.1609/aaaiss.v7i1.36910. A search summary says it reports quantum methods outperforming classical ones; I did not verify this from the full text. — [AAAI](https://ojs.aaai.org/index.php/AAAI-SS/article/view/36910)
- Other credit feature-selection QUBO work found in OpenAlex:
  - Chen, Tso, He, "Quantum Optimized Cost Based Feature Selection and Credit Scoring for Mobile Micro-financing", Computational Economics (2023), DOI 10.1007/s10614-023-10365-8.
  - Schetakis et al., "Quantum Machine Learning for Credit Scoring", Mathematics 12(9):1391 (2024), DOI 10.3390/math12091391.
  - Hellstern, Dehn, Zaefferer, "Quantum computer based feature selection in machine learning", IET Quantum Communication (2024), DOI 10.1049/qtc2.12086.
  - Pranjić, Mummaneni, Tutschku, "Quantum annealing-based feature selection", Neurocomputing (2025), DOI 10.1016/j.neucom.2025.131673.
  - Jin, Ye, Zhu, "Application of Quantum Annealing Algorithm in the Combined Optimization of Credit Score Cards" (2024), DOI 10.1145/3654823.3654914.

  Sources: [Chen](https://doi.org/10.1007/s10614-023-10365-8); [Schetakis](https://doi.org/10.3390/math12091391); [Hellstern](https://doi.org/10.1049/qtc2.12086); [Pranjić](https://doi.org/10.1016/j.neucom.2025.131673); [Jin](https://doi.org/10.1145/3654823.3654914)
- Classical credit-scoring feature selection already uses local search metaheuristics because greedy methods get stuck: Boughaci and Alkhawaldeh, "Three local search-based methods for feature selection in credit scoring" (2018), DOI 10.1007/s40595-018-0107-y. — [DOI](https://doi.org/10.1007/s40595-018-0107-y)

**B. Model / ensemble selection (choose k models)**
- Axyon (an R&D report with a European bank) used a QUBO framework to select predictive models for equity strategies. The report says QUBO-selected ensembles consistently outperform greedy selection in robustness and internal diversification. This is a vendor report, not peer reviewed. — [Axyon technical report](https://axyon.ai//resources/Quantum%20Inspired%20Ensemble%20Optimisation)

**C. Collateral optimization / allocation**
- Giron, Korpas, Parvaiz, Malik, Aspman, "Approaching Collateral Optimization for NISQ and Quantum-Inspired Computing", IEEE Transactions on Quantum Engineering 4 (2023), DOI 10.1109/TQE.2023.3314839. Assets are allocated to cover exposures at minimum cost. The paper gives a MILP formulation and then a QUBO formulation, but only small local tests and no quantitative benchmarks. — [arXiv 2305.16395](https://arxiv.org/abs/2305.16395)
- A 2026 preprint, Jin and Florescu, "A Certified Higher Order Quantum Framework for CSA and Margin-Aware Collateral Optimization", arXiv 2606.04235. It is a higher-order formulation; I read only its OpenAlex metadata. — [DOI](https://doi.org/10.48550/arxiv.2606.04235)
- Related settlement problem: Braine, Egger, Glick, Woerner (Barclays + IBM), "Quantum Algorithms for Mixed Binary Optimization Applied to Transaction Settlement", IEEE TQE (2021), DOI 10.1109/TQE.2021.3063635. It selects which transactions settle subject to balance and collateral constraints. The constraints are linear inequalities, not an exact k. — [DOI](https://doi.org/10.1109/tqe.2021.3063635)

**D. Loan portfolio / securitization pool selection**
- Recent preprints exist, but I verified only their metadata:
  - Bhargava et al., "Loan Portfolio Optimization with Variational Quantum Algorithms", arXiv 2609.30195 (2026).
  - Wang et al., "Quantum computing for loan portfolio pricing optimization", Frontiers in Physics (2026), DOI 10.3389/fphy.2026.1744791.
  - Tang et al., "Quantum computation for pricing the collateralized debt obligations", Quantum Engineering (2021), DOI 10.1002/que2.84. This is pricing via amplitude estimation, not pool selection.

  Sources: [Bhargava](https://doi.org/10.48550/arxiv.2609.30195); [Wang](https://doi.org/10.3389/fphy.2026.1744791); [Tang](https://doi.org/10.1002/que2.84)

**E. Index tracking / hedge-basket selection with k instruments**
- Palmer, Karagiannis, Florence, Rodriguez, Orús, Naik, Mugel (Multiverse Computing authors), "Financial Index Tracking via Quantum Computing with Cardinality Constraints", arXiv 2208.11380 (2022). They add non-linear cardinality constraints and call the resulting problems non-convex, solved by quantum annealing. Applied to enhanced index tracking, they get small portfolios that track the index with a better risk profile. — [arXiv 2208.11380](https://arxiv.org/abs/2208.11380)

**F. Facility location: branch / ATM network (p-median, exactly p sites)**
- p-median local search is hard. With standard neighborhoods it is tight PLS-complete, and local descent can need exponentially many iterations in the worst case, whatever the tie-breaking and pivoting rules. The distribution of local optima was named there as an open direction. — [Alekseeva & Kochetov, "Complexity of local search for the p-median problem" (via EJOR/RePEc listing)](https://ideas.repec.org/a/eee/ejores/v191y2008i3p736-752.html)
- Variable neighborhood search was introduced for p-median because swap local search stalls in local optima: Hansen and Mladenović, "Variable neighborhood search for the p-median", Location Science (1997), DOI 10.1016/S0966-8349(98)00030-8, about 400 citations. A Hansen–Mladenović GERAD report notes that for many problems the local optima are relatively close to one another, i.e. a "big valley". — [DOI](https://doi.org/10.1016/s0966-8349(98)00030-8); [GERAD G-2007-24](https://www.gerad.ca/papers/G-2007-24.pdf)
- The continuous planar p-median objective "may contain several local optima", and good starting solutions significantly improve local search. — [Brimberg & Drezner, arXiv 2004.05510](https://arxiv.org/pdf/2004.05510)
- A fitness landscape analysis of a healthcare facility location problem exists: Scouarnec, Lucet, Tari, Brisoux Devendeville, "Healthcare Facility Location Problem and Fitness Landscape Analysis" (2025), DOI 10.1007/978-3-031-86849-8_14. I found only its metadata, not its findings. — [DOI](https://doi.org/10.1007/978-3-031-86849-8_14)

**G. Scenario / representative selection (k-medoids)**
- k-medoids (PAM) is the p-median objective applied to data points. Its swap-based local search (BUILD + SWAP) is the standard method, and Schubert and Rousseeuw made it faster ("FastPAM"), Information Systems (2021), DOI 10.1016/j.is.2021.101804. Metaheuristics such as BRKGA are proposed for k-medoids because PAM's swap descent ends in local optima: Brito et al., RAIRO-OR (2022), DOI 10.1051/ro/2022141. — [Schubert & Rousseeuw](https://doi.org/10.1016/j.is.2021.101804); [Brito et al.](https://doi.org/10.1051/ro/2022141)

**H. Max-diversification / least-correlated k assets (maximum diversity, densest/sparsest k-subgraph)**
- The Maximum Diversity Problem (choose m of n elements to maximize the sum of pairwise distances) has a dedicated benchmark library, MDPLIB (315 instances; MDPLIB 2.0 from 2021). It has a large metaheuristic literature: Duarte and Martí tabu search (2007), Palubeckis iterated tabu search (2007), Wu and Hao memetic (2013), and a comparison of 10 heuristics and 20 metaheuristics by Martí, Gallego, Duarte (2013). The literature's focus on perturbation and tabu over plain local search is indirect evidence of many swap-local optima. — [Optsicom MDP page](https://grafo.etsii.urjc.es/optsicom/mdp.html); [Martí et al. 2013](https://grafo.etsii.urjc.es/en/publication/marti-2013-heuristics); [Wu & Hao EJOR 2013](https://leria-info.univ-angers.fr/%7Ejinkao.hao/papers/EJORWuHao2013.pdf)
- Densest k-subgraph is hard to approximate within almost-polynomial ratios under ETH (Manurangsi, STOC 2017, DOI 10.1145/3055399.3055412). Strong SDP relaxations have polynomial integrality gaps (Bhaskara et al., SODA 2012). — [Manurangsi](https://doi.org/10.1145/3055399.3055412); [Bhaskara et al.](https://doi.org/10.1137/1.9781611973099.34)
- Maximum Independent Set is cited as relevant to financial services in the IBM 2026 QeMCMC paper discussed under question 3. — [arXiv 2602.06171](https://arxiv.org/abs/2602.06171)

**I. Bank-specific pilots (discrete problems)**
- Barclays + IBM: transaction settlement (mixed binary), as in C above. — [DOI](https://doi.org/10.1109/tqe.2021.3063635)
- CaixaBank-affiliated authors + IBM: Egger, García Gutiérrez, Cahué Mestre, Woerner, "Credit Risk Analysis Using Quantum Computers", IEEE Transactions on Computers (2020), DOI 10.1109/TC.2020.3038063. This is amplitude estimation, not combinatorial selection. — [DOI](https://doi.org/10.1109/tc.2020.3038063)
- American Express: feature selection for fraud and default (A above). — [AAAI](https://ojs.aaai.org/index.php/AAAI-SS/article/view/36910)
- HSBC + IBM: bond-trading fill-probability prediction with quantum ML, Ciceri et al., arXiv 2509.17715 (2025). This is ML, not a k-of-n problem. A 2026 preprint by Faryad argues that such hardware QML claims should be tested against a null circuit. — [HSBC arXiv](https://doi.org/10.48550/arxiv.2509.17715); [Faryad](https://doi.org/10.48550/arxiv.2610.41268)
- Raiffeisen Bank International + Reply: a QUBO portfolio problem on a production-like bank dataset with quantum annealing, with results consistent with the exact global optimum. A Qkrishi-bank study (arXiv 2504.08843) did discrete asset selection by D-Wave hybrid CQM, then classical weights. The authors say explicitly that it does not show quantum advantage. — [arXiv 2504.08843](https://arxiv.org/html/2504.08843v2); [review arXiv 2604.08180](https://arxiv.org/pdf/2604.08180)
- BBVA with IBM: VQE/QAOA portfolio optimization demos, reported in a secondary roundup. BNP Paribas with Classiq: portfolio optimization. — [Quantum Insider 2026 roundup](https://thequantuminsider.com/2026/03/27/15-plus-global-banks-probing-the-wonderful-world-of-quantum-technologies/embed/)
- Intesa Sanpaolo: an experience report, Sotelo et al., IEEE Engineering Management Review (2024), DOI 10.1109/EMR.2024.3373796. — [DOI](https://doi.org/10.1109/emr.2024.3373796)
- Surveys: Herman, Googin, Liu, Sun et al., "Quantum computing for finance", Nature Reviews Physics (2023), DOI 10.1038/s42254-023-00603-1 (JPMorgan-led; about 370 citations). Also the earlier arXiv survey 2201.02773. — [DOI](https://doi.org/10.1038/s42254-023-00603-1); [arXiv survey](https://doi.org/10.48550/arxiv.2201.02773)

### Inferences
- **Coupling structure of MI/correlation feature-selection QUBOs.** This is inferred from the descriptions "importance vs. redundancy / independence, weighted by α"; I did not see the exact matrices in the full texts. In the Milne and Mücke style, the diagonal is h_i = −α·relevance_i (negative, rewarding selection). The off-diagonal is J_ij = (1−α)·redundancy_ij, which is ≥ 0 for mutual information or absolute correlation, so every coupling is repulsive. With exactly k selected, this is a maximum-diversity / "sparsest-k-subgraph with vertex weights" problem. That gives frustration through the constraint rather than through mixed-sign couplings. Mixed-sign couplings do appear if one uses signed correlations, or conditional MI, where the synergy term I(x_i;y|x_j) − I(x_i;y) can be negative. The task brief claims mixed-sign couplings; that holds for conditional-MI/synergy variants, not for the plain MI-redundancy QUBO.
- **Order of each objective.**
  - Native quadratic: feature selection (MI/correlation), max-diversity, densest/sparsest k-subgraph, ensemble selection with pairwise error-correlation.
  - Higher-order: p-median and k-medoids. Their cost Σ_c w_c · min_{s ∈ S} d(c,s) is a min over selected sites, so it is not quadratic in x unless one adds assignment variables y_cs (n×m extra qubits). For n ≈ 12–20 candidate sites that is impractical on QeMCMC hardware. It can be expanded into an exact higher-order pseudo-Boolean polynomial instead.
  - Wrapper-loss feature selection (VarQFS-style) is black-box, all-orders.
  - Collateral and settlement are mixed binary/integer problems with inequality constraints, so they are not natural k-of-n.
- **Fit to QeMCMC with swap moves.** Ranked by fit:
  1. MI-redundancy credit feature selection on German Credit.
  2. Max-diversification / least-correlated k assets.
  3. k-medoids stress-scenario selection.
  4. p-median branch siting.
  5. Index tracking.

  Collateral, settlement and loan-pool problems are poor fits at n ≈ 12–20, because their constraints are inequalities and budgets rather than an exact count.
- **Public data for n ≈ 12–20 instances.**
  - UCI German Credit (20 attributes) is ideal: n = 20, choose k = 5–8.
  - UCI Taiwan default-of-credit-card (23 features) and Australian Credit (14 features) are other options.
  - Index tracking and max-diversification can reuse the team's existing ETF price data. Use a correlation or distance matrix instead of Σ.
  - Scenario selection: historical quarterly windows, which the project already has as 64 windows, can be clustered to choose k representative stress windows.
  - Branch siting: public bank branch locations (e.g. FDIC Summary of Deposits) plus census population. This is a dataset suggestion I did not verify within this research.

### Gaps
- I could not read the full texts of Milne 2017, Mücke 2023 or Giron 2023, so the exact coefficient signs, α values and whether Σx = k is enforced by penalty are unverified.
- I found no published local-optima counts under swap moves for credit feature-selection QUBOs, max-diversity at small n, or p-median at n ≤ 20. The literature gives worst-case complexity and metaheuristic necessity, not small-n landscape statistics. The team will need to measure these with its own `landscape.py`.
- I did not find primary sources for the JPMorgan, Goldman Sachs, Wells Fargo, Itaú, Crédit Agricole/Pasqal or HSBC discrete k-of-n pilots within budget. Searches returned only secondary roundups or unrelated work.
- I did not search CDO tranche pool construction or pairs/cointegration basket selection specifically, and found no quantum QUBO paper on them.
- I did not search fraud-rule subset selection specifically, apart from the American Express feature-selection paper.

## Key question 2: Which have the strongest evidence of multi-modal landscapes under swap moves at small n?

### Takeaway
The strongest classical evidence is for p-median / k-medoids, whose swap local search is PLS-complete, motivated VNS, and has known multiple local optima, and for maximum-diversity / densest-k-subgraph, which has a large tabu and memetic literature and is inapproximable. The quantum feature-selection papers report solution quality, not landscape statistics. The team's single-optimum finding on ETF mean-variance has a likely structural cause (see Inferences), which also suggests which modifications create ruggedness.

### Cited Findings
- p-median local search with standard neighborhoods is tight PLS-complete, with exponential worst-case descent. — [Alekseeva & Kochetov (EJOR 2008 listing)](https://ideas.repec.org/a/eee/ejores/v191y2008i3p736-752.html)
- VNS was designed for p-median to escape swap local optima; for many problems the local optima cluster close together (a big valley). — [Hansen & Mladenović 1997](https://doi.org/10.1016/s0966-8349(98)00030-8); [GERAD G-2007-24](https://www.gerad.ca/papers/G-2007-24.pdf)
- The planar p-median "may contain several local optima". — [Brimberg & Drezner](https://arxiv.org/pdf/2004.05510)
- Maximum diversity: 30 heuristics and metaheuristics were compared on 315 benchmark instances, and the state of the art uses tabu search with constrained swap neighborhoods plus perturbation. — [Martí et al. 2013](https://grafo.etsii.urjc.es/en/publication/marti-2013-heuristics); [Wu & Hao 2013](https://leria-info.univ-angers.fr/%7Ejinkao.hao/papers/EJORWuHao2013.pdf)
- Local Optima Networks (LONs) are the standard tool to quantify the number and connectivity of local optima. Swap (1-swap) neighborhoods have been analyzed with LONs, and an optimum for one neighborhood need not be one for another. — [Ochoa et al., LON model arXiv 1402.2959](https://arxiv.org/pdf/1402.2959); [multi-layer LON arXiv 2004.13936](https://arxiv.org/pdf/2004.13936)
- Palmer et al. call cardinality-constrained index tracking "non-convex". — [arXiv 2208.11380](https://arxiv.org/abs/2208.11380)

### Inferences
- **Why the ETF k=5-of-16 problem is unimodal (inferred).** ETF returns share a dominant market factor, so Σ ≈ β βᵀ σ_m² + D. Under a fixed k, the quadratic term then depends mostly on Σ β_i x_i (nearly separable after a rank-1 correction). Swap moves see an almost linear objective with a single basin. Ruggedness needs couplings that differ in sign or strength across pairs without a single dominant mode. Examples:
  - a correlation-distance or thresholded-correlation graph (max-diversity / independent set), and
  - MI redundancy among heterogeneous credit features (categorical plus numeric with clustered dependencies).
- **Cheap experiments for the team, in order of expected ruggedness:**
  1. Max-diversity on the same 16 ETFs, using the correlation distance d_ij = √(2(1−ρ_ij)) or −|ρ_ij|, k = 5. This is a pure repulsive QUBO, and frustration comes from the cardinality constraint.
  2. Thresholded correlation graph to maximum k-independent-set or densest-k-subgraph. This is closest to the IBM 2026 MIS QeMCMC work.
  3. German Credit MI-redundancy QUBO, n = 20, k = 5–8.
  4. k-medoids over 16 assets or 16 windows (higher-order).

  For each, measure the number of swap-local minima by exhaustive enumeration: C(16,5) = 4368 and C(20,6) = 38760 states, both trivial with the existing StateSpace machinery.
- **Market-neutralized covariance.** Removing the first principal component from Σ before building the QUBO should break the near-separability and may create multiple optima. This is a hypothesis to test.

### Gaps
- No source gives local-optima counts at n ≈ 12–20 for any of these problems. Enumeration is required.
- I did not fetch the Scouarnec et al. 2025 facility-location landscape results.

## Key question 3: Which have the most natural "need for sampling" (Boltzmann sampling of near-optimal solutions)?

### Takeaway
The natural sampling use cases are:
- feature selection, where you want a distribution over near-optimal subsets for feature-importance stability and model averaging;
- stress-scenario / k-medoids selection, where many near-equivalent representative sets exist and robustness across them matters; and
- ensemble or model selection, which needs diversity across good ensembles.

These need samples from exp(−E/T), not one argmin, which is the regime where QeMCMC (Layden et al. 2023) is defined. IBM's 2026 follow-up applies QeMCMC with parallel tempering to MIS, a problem whose relevance to financial services that paper itself points out.

### Cited Findings
- Layden, Mazzola, Mishmash, Motta et al., "Quantum-enhanced Markov chain Monte Carlo", Nature 619 (2023), DOI 10.1038/s41586-023-06095-4. — [DOI](https://doi.org/10.1038/s41586-023-06095-4)
- Marshall, Egger, Garn, Schiavello, Brandhofer, Zoufal, Woerner (IBM), "Quantum-enhanced Markov Chain Monte Carlo for Combinatorial Optimization", arXiv 2602.06171 (Feb 2026, v2 Mar 2026). QeMCMC plus warm-starting and parallel tempering on Maximum Independent Set recovers global optima for instances of up to 117 variables on IBM hardware. They report "early evidence" of a scaling advantage over similar classical methods, and the abstract cites MIS relevance in financial services. — [arXiv 2602.06171](https://arxiv.org/abs/2602.06171)
- Limits on speedup: Orfi and Sels, "Bounding the speedup of the quantum-enhanced Markov-chain Monte Carlo algorithm", Phys. Rev. A 110, 052414 (2024), DOI 10.1103/PhysRevA.110.052414. Related work:
  - Hsieh, Orfi, Sels, "Adiabatic dressing of quantum-enhanced Markov chains" (2026), DOI 10.1103/x255-fw2l.
  - Ferguson and Wallden, QeMCMC for systems larger than the device, Phys. Rev. Research 7, 013231 (2025).
  - Nakano et al., QAOA-enhanced MCMC, Phys. Rev. Research 6, 033105 (2024).

  Sources: [Orfi & Sels](https://doi.org/10.1103/physreva.110.052414); [Hsieh et al.](https://doi.org/10.1103/x255-fw2l); [Ferguson & Wallden](https://doi.org/10.1103/physrevresearch.7.013231); [Nakano et al.](https://doi.org/10.1103/physrevresearch.6.033105)
- Model-ensemble QUBO selection is motivated by robustness and diversification of the selected set, which is a distributional concern. — [Axyon report](https://axyon.ai//resources/Quantum%20Inspired%20Ensemble%20Optimisation)
- VarQFS (Zoufal et al.) optimizes a parameterized distribution over feature subsets rather than a single subset. — [Quantum 7, 909](https://quantum-journal.org/papers/q-2023-01-26-909/)

### Inferences
- **Recommended pivot.** The fastest route is to keep the ETF data and switch to a max-diversification or thresholded-correlation MIS / densest-k-subgraph k-of-16 QUBO. It reuses the pipeline, has repulsive couplings that create frustration under the cardinality constraint, and directly echoes IBM's 2026 MIS QeMCMC finance framing.
- **Second option.** German Credit MI-redundancy feature selection (n = 20) is the best "banking" story with prior quantum literature: 1QBit, IBM, American Express.
- **Sampling, not just optimizing.** Frame both as Boltzmann sampling of good subsets. Then evaluate mixing time, the effective sample size across distinct local optima, and the probability mass on the top-m subsets, not just time-to-optimum.
- **Hardware caution.** Exact-k sampling on hardware needs either penalty terms, which distort the landscape, or swap-preserving (XY / Dicke-subspace) proposals. QeMCMC's Ising-evolution proposal does not natively conserve Hamming weight, so expect a rejection overhead. This is a design inference, not a sourced claim.

### Gaps
- No published QeMCMC study targets a finance k-of-n problem directly. The IBM 2026 paper works on MIS and only mentions finance.
- The page I read did not describe how Marshall et al. handled constraints. Their full text should be read for the penalty or proposal design.
- I did not find any published comparison of QeMCMC and Metropolis–Hastings mixing on cardinality-constrained feature-selection QUBOs.
