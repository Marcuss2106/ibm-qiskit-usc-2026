# Literature review

Citations use (Author Year); full entries are in [`references.md`](references.md).
**[abs]** = claim taken from the abstract only; **[full]** = read in full text;
**[meta]** = cited for its well-known standard content, not re-read here.

Notation used throughout: x is the 8-bit asset-selection vector, B = 3 the number of assets
to hold, μ and Σ the annualized mean returns and covariance, λ the risk weight, ρ the
penalty weight, and T the MCMC temperature.

---

## 1. Problem formulation: portfolio selection as a QUBO

**Foundations.** Mean–variance selection originates with Markowitz (1952) [meta]. Its
binary, cardinality-constrained form is a standard QUBO. Lucas (2014) [meta] catalogues
Ising encodings of NP problems, including the squared-penalty construction for "choose
exactly B". Glover, Kochenberger & Du (2019; expanded 2022) [meta] is the standard tutorial
on turning constraints into quadratic penalties.

**Portfolio-specific QAOA.** Brandhofer et al. (2022) [abs] formulate exactly our problem —
"quadratic binary optimization constrained on the number of assets" — and study choices of
variational form, classical optimizer, shot noise, and gate/readout error. They also propose
a criterion separating "easy" and "hard" instances. Hodson et al. (2019) [abs] treat an
eight-stock rebalancing problem with hard-constraint mixers and report portfolios "within 5 %
of the optimal adjusted returns" on an ideal simulator — the closest size analogue to our
8-asset universe.

**Penalty design is not neutral.** Lozano (2026) [abs] shows on D-Wave annealers that the
exact cardinality penalty adds a dense rank-one term that makes the interaction graph
complete, with zero feasible raw samples at every tested scale; enforcing cardinality
classically afterwards worked far better. Kurebayashi et al. (2025) [abs] summarize the
tension: "too small yields infeasibility, too large harms solution quality." Giovagnoli
(2025) [abs] covers penalty encoding as part of the QAOA pipeline.

### Implication for our build (`portfolio.py`, `encoding.py`)

Our objective matches the literature form:

$$
F(x) = \frac{\lambda}{B^2}\, x^\top \Sigma x \;-\; \frac{1}{B}\, \mu^\top x \;+\; \rho \Big(\sum_i x_i - B\Big)^2
$$

Because the weights are x / B even for infeasible x, selecting *more* than three assets
implies leverage above 1 and makes the return term more negative. The penalty therefore
has to beat a real incentive, not just break ties.

Let F_obj be F without the penalty term and F*_feas the best feasible value. The smallest
penalty that keeps every infeasible state above the feasible optimum is:

$$
\rho_{\min} = \max_{x \,:\, \sum_i x_i \neq B} \; \frac{F^{*}_{\text{feas}} - F_{\text{obj}}(x)}{\big(\sum_i x_i - B\big)^2}
$$

Compute it by enumerating all 256 states at each rebalance date, then use ρ ≈ 1.5–2 × ρ_min
rather than a very large value (section 3 explains why a large ρ also hurts QeMCMC).

---

## 2. QAOA (comparison method)

**Origin and mechanics.** Farhi, Goldstone & Gutmann (2014) [meta] introduce QAOA. Zhou et
al. (2020) [abs] give parameter-initialization heuristics and a resource analysis, noting
that random initialization becomes expensive as depth grows — irrelevant at depth 1, where
a grid search is cheap. Giovagnoli (2025) [abs], the study guide's Paper 2, proves symmetry
and periodicity of the energy landscape and proposes a parameter-space reduction. Blekos et
al. (2024) [meta] is a comprehensive review of variants.

**Better aggregation.** Barkoutsos et al. (2020) [abs] argue that for diagonal (classical)
Hamiltonians the mean energy is the wrong training objective. They propose the conditional
value-at-risk (CVaR) of the sampled energies — the average of the best fraction of shots —
and report "faster convergence to better solutions for all combinatorial optimization
problems tested."

**Constraint-preserving variants.** Hadfield et al. (2019) [meta] generalize QAOA to the
Quantum Alternating Operator Ansatz with feasibility-preserving mixers. Wang et al. (2020)
[abs] show XY mixers give "a significant improvement over the general X mixer." Bärtschi &
Eidenbenz (2019) [meta] give deterministic preparation of the Dicke state, the equal
superposition of every 3-of-8 portfolio:

$$
\lvert D^{8}_{3} \rangle = \frac{1}{\sqrt{56}} \sum_{x \,:\, \lvert x \rvert = 3} \lvert x \rangle
$$

Their Grover-mixer paper (2020) [abs] applies this to discrete portfolio rebalancing and
reports outperforming earlier QAOA approaches. Mancilla et al. (2026) [abs] apply Dicke
initialization with an XY mixer to cardinality-constrained portfolios and backtest against
simulated annealing and HRP. Their headline Sharpe ratios come from a single year of 10
equities with 76.8 % turnover, so they illustrate the setup rather than establish
performance.

**Warm starts.** Egger, Mareček & Woerner (2021) [meta] warm-start QAOA from relaxed
classical solutions — the research line that motivates Marshall et al.'s warm-started
QeMCMC.

### Implication for our build (`qaoa.py`)

- With an X mixer and the uniform starting state, only 56 / 256 ≈ 21.9 % of the initial
  distribution is feasible. Log the feasible fraction of the final 1,500 shots; a low
  fraction is the main expected weakness of depth-1 penalty QAOA.
- Cheap, literature-backed upgrades if time permits:
  1. Optimize CVaR instead of the mean (Barkoutsos 2020).
  2. A constraint-preserving run (Dicke start plus XY ring mixer), reported as a separate
     variant so the "identical QUBO" comparison stays intact.
- Count the angle search as cost: 3 starts × at most 60 exact-expectation calls = at most
  180 objective evaluations.

---

## 3. QeMCMC (main method)

**Layden et al. (2023), *Nature* [full].** The original algorithm. Each step prepares the
current bitstring s, evolves it for time t under a weighted sum of the problem Hamiltonian
and a transverse-field mixer, and measures once to get the proposal s′:

$$
H = (1-\gamma)\,\alpha\, H_{\text{prob}} + \gamma \sum_j X_j ,
\qquad
\alpha = \frac{\lVert H_{\text{mix}} \rVert_F}{\lVert H_{\text{prob}} \rVert_F}
= \frac{\sqrt{n}}{\sqrt{\sum_{j<k} J_{jk}^2 + \sum_j h_j^2}}
$$

The factor α puts both terms on a common scale. Because H is real and symmetric, the chance
of proposing s′ from s equals the chance of proposing s from s′. That symmetry lets the plain
Metropolis rule accept the move without a proposal correction:

$$
A(s \to s') = \min\!\Big(1,\; e^{-\left(E(s') - E(s)\right)/T}\Big)
$$

Layden et al. do not optimize γ and t; they draw them "uniformly at random in each
iteration" (ranges are in the Supplementary Material). On fully connected SK-type instances
with up to 10 spins at T = 1, the spectral gap shrinks as 2^(−kn) with k ≈ 0.26 for the
quantum proposal versus k ≈ 0.94–0.95 for local and uniform classical proposals. The
hardware run (ibmq_mumbai, 10 spins) used a randomly compiled **second-order** Trotter
formula. Noise slows convergence but does not break correctness, because accept/reject is
classical; full depolarization reduces the method to a uniform proposal.

**Marshall et al. (2026) [full].** Moves QeMCMC from Boltzmann sampling to optimization:
Maximum Independent Set with up to 117 qubits on IBM Heron devices, recovering the global
optimum for all five instances. Key differences from Layden:

- First-order Trotter with two steps, equivalent to depth-2 QAOA with tied angles.
- **Asymmetric** proposals, which the authors acknowledge void the convergence guarantees.
- Warm start through softened Ry rotations seeded from the last accepted state.
- 10,000 shots per iteration; the ~10 lowest-energy samples are kept and one is subsampled.
- Five-replica parallel tempering at T = 0.01, 0.11, 0.21, 0.51 and 1.01.

Replicas i and j at temperatures T_i and T_j swap states with probability:

$$
P_{\text{swap}} = \min\!\Big(1,\; \exp\!\Big[\Big(\tfrac{1}{T_i} - \tfrac{1}{T_j}\Big)\big(E(s_j) - E(s_i)\big)\Big]\Big)
$$

The baseline is classical replica-exchange MCMC with uniform multi-bit flips, and the metric
is median iterations to the CPLEX optimum. Scaling evidence is a fitted exponential over five
instances. The authors call the method "purely a heuristic one" without provable convergence.

**Follow-ups and critiques.**

- **Orfi & Sels (2024, PRA) [abs]:** "no speedup over classical sampling on a worst-case
  unstructured sampling problem"; an upper bound on the Markov gap "rules out a speedup for
  any unital quantum proposal."
- **Hsieh, Orfi & Sels (2026, PRA) [abs]:** the core trade-off — the quantum dynamics must
  spread out enough to propose non-local moves, but "excessive delocalization produces
  configurations unlikely to be accepted." Adiabatic dressing improves the Markov gap.
- **Nakano et al. (2024, PRR) [abs]:** QAOA-type proposal circuits that stay symmetric for
  any parameters. The **measurable acceptance rate correlates with the spectral gap** in a
  parameter range, so it can be used to tune parameters.
- **Ferguson & Wallden (2025, PRR) [abs]:** coarse-grained QeMCMC using far fewer qubits than
  spins.
- **Arai & Kadowaki (2025, Sci. Rep.) [abs]:** annealing-based proposals. **Cao et al. (2026)
  [abs, preprint]:** breaking detailed balance can accelerate quantum MCMC.

### Implication for our build (`qemcmc.py`)

- **Naming.** The roadmap's κ is Layden's γ (Marshall also calls it κ). Keep α explicit in
  the code.
- **Penalty interaction.** α is computed from the norm of the *whole* cost Hamiltonian, so a
  large ρ inflates that norm and shrinks the effective weight of the return and risk terms
  in the proposal. Keep ρ near its minimum, or compute α from the objective part only, and
  document the choice.
- **Tuning.** Following Nakano et al., log the acceptance rate and choose κ, t and T on
  development data so acceptance is moderate — not near 0 or 1.
- **Baselines.** Add uniform-proposal and single-bit-flip classical MCMC chains with the
  same T, step count and seeds. Both Layden and Marshall report exactly this comparison;
  without it the "quantum proposal" claim cannot be tested.
- **Attribution.** Credit the algorithm to Layden (2023). Cite Marshall (2026) for the
  optimization framing and as the source of the optional warm-start and tempering
  extensions.

---

## 4. Fair solver comparison

Hellstern, Schacht & Zaefferer (2026) [abs], the study guide's Paper 4, compared solvers on
180 instances with 14–48 variables:

- Branch-and-cut matched every reference and certified 176 within 600 s.
- With optima moved to random bitstrings at 48 variables, branch-and-cut found 4 of 10 and
  certified none, while parallel tempering reached every optimum in every run within 60 s.
- LR-QAOA "offer[s] no solution-quality improvement" over the classical comparators.
- Harder Wishart instances from 72 variables up defeated all classical methods, but "this
  does not provide evidence for quantum advantage."

Classical baselines worth naming: simulated annealing (Kirkpatrick et al. 1983), parallel
tempering (Earl & Deem 2005), and Metropolis (1953) / Hastings (1970) sampling. The Quantum
Optimization working-group report (Abbas et al. 2023) [meta] sets out benchmarking good
practice.

### Implication for our build (`metrics.py`, scorecard)

- With 8 assets, exact enumeration gives the certified optimum. Report each method's gap to
  it, F(x_alg) − F*_feas, as planned, and treat runtime numbers as descriptive only.
- Hellstern et al.'s gauge-randomization idea is cheap here: permute the asset order once
  and confirm both methods' results are unchanged up to relabeling. This checks that the
  encoding, not qubit ordering, drives the result.

---

## 5. Finance methodology (estimation and backtest)

- **Estimation error dominates.** Chopra & Ziemba (1993) [meta]: errors in means matter far
  more than errors in variances and covariances. Merton (1980) [meta]: expected returns are
  hard to estimate from short windows. A 252-day mean estimate is very noisy.
- **Covariance shrinkage.** Ledoit & Wolf (2004) [meta]: blending the sample covariance with
  a structured target improves out-of-sample portfolios. Available as
  `sklearn.covariance.LedoitWolf`.
- **Naive benchmark.** DeMiguel, Garlappi & Uppal (2009) [meta]: across many datasets,
  optimized portfolios rarely beat equal weighting (1/N) out of sample once estimation error
  is counted.
- **Overfitting.** Bailey & López de Prado (2014) [meta]: the deflated Sharpe ratio corrects
  for the number of strategies tried. Bailey et al. (2016) [meta]: the probability of
  backtest overfitting.
- **Surveys.** Egger et al. (2020) [abs], the study guide's Paper 1, and Herman et al. (2023,
  *Nat. Rev. Phys.*) [meta] place portfolio optimization among candidate quantum-finance
  applications while stressing end-to-end costs.

### Implication for our build (`returns.py`, `backtest.py`, `metrics.py`)

- Add two zero-cost baselines to the scorecard: equal weight across all 8 ETFs (true 1/N),
  and the exact-enumeration optimal 3-asset portfolio.
- If time allows, run a Ledoit–Wolf covariance variant as a sensitivity check.
- With only N = 24 monthly test returns, report the Sharpe ratio with its standard error.
  A common approximation, in per-period units, is:

$$
\mathrm{SE}\big(\widehat{SR}\big) \approx \sqrt{\frac{1 + \tfrac{1}{2}\widehat{SR}^{2}}{N}}
$$

- State how many configurations (λ, κ, t, T settings) were tried, per Bailey & López de
  Prado.

---

## 6. What the literature does *not* support claiming

- Any quantum speedup with 8 assets (Orfi & Sels 2024; Hellstern et al. 2026; the problem is
  trivially enumerable).
- That Marshall et al.'s MIS results transfer to portfolios (different problem, asymmetric
  proposals, parallel tempering, 10k shots).
- That a lower in-sample objective implies better out-of-sample returns (Chopra & Ziemba;
  DeMiguel et al.). The roadmap already separates these; keep it that way in the
  presentation.
