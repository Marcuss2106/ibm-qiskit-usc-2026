# Pilot: Bayesian factor selection for SPY (bead a78, branch `pilot/factor-selection`)

**Question.** Choosing k of n factors to explain SPY's daily returns is a discrete,
fixed-count sampling problem where MCMC is the standard tool. Does it meet the
conditions under which MCMC, and a quantum proposal, are strong?

**Setup** (`qemcmc/factors.py`, `python -m qemcmc.factors`). Factors, fixed before
running, none of them SPY components: changes in VIX and 13-week/5-/10-/30-year yields;
returns of HYG, LQD, TIP, UUP, DBC, USO, GLD, SLV, FXY; plus EFA and EEM in the "all"
universe. Same 64 quarterly 252-day windows. Score = exact log posterior of each subset
(Zellner g-prior, g = N, uniform over k-subsets), sampled at its natural T = 1. Circuit
phase = first-order pairwise approximation of R².

**Results (5 of 14 non-equity / 5 of 16 all).**

| Condition for MCMC strength | Non-equity | All | Met? |
|---|---|---|---|
| Several separated modes (windows with more than 1 local optimum) | 11% (max 2) | 3% (max 2) | No |
| Greedy fails from many starts (median success) | 1.00 | 1.00 | No |
| Posterior mass spread across modes (median mass outside the top mode) | 0.000 | 0.000 | No |
| Posterior spread within a mode (effective number of subsets, out of 2002 / 4368) | 16.7 | 5.4 | Weakly |
| Swap chain mixes slowly (spectral gap at T = 1, median) | 0.039 | 0.024 | No (fast) |
| Quantum proposal mixes faster than swaps (gap ratio, median) | 0.25 | 0.12 | No |

The score is not pairwise (rank correlation of the first-order approximation with exact
R² is 0.23 and −0.31: strongly correlated yields break the expansion). `fitted_phase.py`
replaces it with the best least-squares pairwise phase (rank correlation 0.99); the
quantum/swap gap ratio is still 0.17–0.41. The approximation is not the cause.

**Verdict.** No. Factor selection for SPY is a sampling problem in form, but on real data
its posterior is one sharp mode around a few subsets; local swaps mix fast and longer
quantum jumps are mostly rejected. Same mechanism as the portfolio problem: a dominant
common structure (here: equity-like and credit factors explain most of SPY) makes the
landscape single-peaked.
