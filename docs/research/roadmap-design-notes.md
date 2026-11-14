# Roadmap design notes

One row per roadmap decision: what the literature says, the risk, and a concrete check.
Severity: **H** = could invalidate a result, **M** = affects quality or fairness,
**L** = polish.

## Reference formulas

The tables below refer to these by name.

**Objective.** x is the 8-bit selection vector, B = 3, weights w = x / B:

$$
F(x) = \frac{\lambda}{B^2}\, x^\top \Sigma x \;-\; \frac{1}{B}\, \mu^\top x \;+\; \rho \Big(\sum_i x_i - B\Big)^2
$$

**Minimum penalty.** F_obj is F without the penalty term; F*_feas is the best feasible value:

$$
\rho_{\min} = \max_{x \,:\, \sum_i x_i \neq B} \; \frac{F^{*}_{\text{feas}} - F_{\text{obj}}(x)}{\big(\sum_i x_i - B\big)^2}
$$

**QeMCMC proposal Hamiltonian** (Layden 2023; the roadmap's κ is Layden's γ):

$$
H = (1-\kappa)\,\alpha\, H_{\text{cost}} + \kappa \sum_j X_j ,
\qquad
\alpha = \frac{\lVert \sum_j X_j \rVert_F}{\lVert H_{\text{cost}} \rVert_F}
$$

**Proposal symmetry.** Q is the matrix of proposal probabilities from the circuit U:

$$
Q_{s' s} = \big\lvert \langle s' \rvert U \lvert s \rangle \big\rvert^{2}, \qquad Q = Q^\top \text{ required}
$$

**Trading cost** at 10 bp per unit of traded weight, against drifted holdings:

$$
\text{cost} = 0.001 \sum_i \big\lvert w_i^{\text{new}} - w_i^{\text{drift}} \big\rvert
$$

## Objective and encoding (`portfolio.py`, `encoding.py`)

| Roadmap choice | Literature | Risk | Suggested check / alternative | Sev |
|---|---|---|---|---|
| Objective F with B = 3 and w = x / B | Markowitz 1952; Brandhofer 2022; Lucas 2014 | Infeasible x imply leverage ≠ 1, so over-selection is *rewarded* by the return term | Fine as-is; document that F is only meaningful on feasible x | L |
| Count penalty ρ, "verify sufficient penalty on 256 states" | Glover 2019; Lozano 2026; Kurebayashi 2025 | Too small → infeasible optimum. Too large → flattened landscape for QAOA and weaker objective signal in QeMCMC (via α) | Compute ρ_min by enumeration (formula above); use 1.5–2 × ρ_min; recompute at every rebalance date since μ and Σ change | **H** |
| λ = 1 | — | In annual units, λ sets the return/risk balance; selection may be dominated by expected return | Plot the 56 feasible portfolios as return vs. volatility and mark where λ = 1 lands; optional λ sweep for the trade-off view in `app.py` | M |
| Direct scores match circuit energies on all 256 states; 56 feasible | C(8, 3) = 56 ✔ | Sign or offset errors in the QUBO → Ising mapping | Keep this test; also check that the enumeration minimum and the Ising-diagonal minimum are the same state | M |
| Sample μ and Σ from 252 days | Chopra & Ziemba 1993; Merton 1980; Ledoit & Wolf 2004 | Mean estimates are very noisy and drive the selection | Optional Ledoit–Wolf covariance sensitivity; never tune on 2024–25 | M |

## QeMCMC (`qemcmc.py`)

| Roadmap choice | Literature | Risk | Suggested check / alternative | Sev |
|---|---|---|---|---|
| Symmetric second-order cost + X-mixer evolution, one shot per proposal, Metropolis | **Layden 2023** (exact match); Marshall 2026 uses asymmetric first-order proposals with filtering | Attribution: the roadmap cites Marshall, but the mechanism is Layden's | Cite Layden 2023 for the algorithm; Marshall 2026 for the optimization framing and extensions | M |
| Proposal symmetry | Layden 2023: holds when H is real and symmetric | A second-order Trotter circuit keeps the symmetry only if its gate sequence is palindromic | Unit test: build Q for the 8-qubit circuit and assert Q = Qᵀ (formula above) | **H** |
| κ = 0.4, t = 5 | Layden draws γ and t at random each step; Nakano 2024: acceptance rate tracks spectral gap | Fixed values may spread the state too much or too little (Hsieh 2026) | Log acceptance rate; tune κ and t on 2018–22 data for moderate acceptance; optionally randomize per step like Layden | M |
| α normalization | Layden 2023 (formula above) | If ρ dominates the cost-Hamiltonian norm, return and risk barely shape proposals | Decide whether α uses the full cost Hamiltonian or the objective part only; record the choice in the output schema | M |
| T = 0.05 in annual objective units | Layden: T relative to unit-variance couplings; Marshall: ladder from 0.01 to 1.01 | T only means something relative to the spread of feasible F values (likely 0.01–0.1) | Report the standard deviation of F over the 56 feasible states per date; set T as a fraction of it | M |
| 3 chains × 500 steps = 1,500 proposals | Marshall: median iterations to optimum | With only 56 feasible states, chains may hit the optimum quickly and make the comparison trivial | Also report the first step at which each chain finds its best feasible state; add the classical baselines below | M |
| No classical MCMC baseline | Layden and Marshall both compare against uniform and local classical proposals | No way to tell whether the quantum proposal adds anything | Add uniform-random and single/double-bit-flip proposal chains with identical T, steps and seeds | **H** |
| Optional extensions | Marshall 2026: Ry warm start, 5-replica parallel tempering | Breaks symmetry; changes the method | Only as clearly labeled variants, after the MVP | L |

## QAOA (`qaoa.py`)

| Roadmap choice | Literature | Risk | Suggested check / alternative | Sev |
|---|---|---|---|---|
| Depth 1, uniform start, X mixer, same QUBO | Farhi 2014; Brandhofer 2022 | Only 56 / 256 ≈ 22 % of the starting state is feasible, and it may stay low | Log the feasible fraction of the 1,500 shots; report the best feasible sample by F and any "no feasible sample" failures | **H** |
| 3 seeded starts × up to 60 calls, exact expectation | Zhou 2020; Giovagnoli 2025 (symmetry and periodicity shrink the angle domain) | Calls wasted on equivalent angle regions | Restrict the two angles to the reduced periodic domain; a coarse grid at depth 1 is a cheap sanity check | L |
| Mean-energy training objective | Barkoutsos 2020 (CVaR) | The mean is dominated by high-penalty infeasible states | Optional CVaR variant averaging the best 10–25 % of shots | M |
| X mixer with penalty | Hadfield 2019; Wang 2020; Bärtschi & Eidenbenz 2019, 2020; Mancilla 2026 | The penalty distorts the landscape | Stretch goal: Dicke-state start with an XY ring mixer, reported as a separate variant | L |

## Evaluation (`backtest.py`, `metrics.py`, `app.py`)

| Roadmap choice | Literature | Risk | Suggested check / alternative | Sev |
|---|---|---|---|---|
| Develop 2018–22, validate 2023, test 2024–25 monthly | Bailey & López de Prado 2014, 2016 | 24 test months give a wide Sharpe confidence interval; many tried settings inflate results | Freeze settings before touching 2024; report how many configurations were tried; show Sharpe with its standard error | M |
| Compare QeMCMC vs QAOA only | DeMiguel 2009; Hellstern 2026 | No reference point for "good" | Add equal weight (1/N) over all 8 ETFs and the exact-enumeration optimum as baselines | **H** |
| 10 bp per unit traded weight, next-day execution, drifted holdings | Standard practice (cost formula above) | — | Keep; also report gross returns so the cost impact is visible | L |
| Resource scorecard | Hellstern 2026 (quality, certification and cost are separate measures) | Mixing shots, calls and wall-clock time | Keep units separate as planned: proposals, shots, objective calls, circuit jobs, two-qubit gates, runtime | L |
| Robustness | Hellstern 2026 (gauge randomization) | Hidden dependence on asset or qubit order | Permute the asset order once; results must match up to relabeling | L |
