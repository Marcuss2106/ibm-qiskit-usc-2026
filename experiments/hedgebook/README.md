# Pilot: multi-factor hedge book (bead xyi, branch `pilot/factor-selection`)

**Question.** Do real instruments spanning several risk factors, with natural hedges,
produce the rugged, competing-hedge landscape where QeMCMC beat single swaps on the
difficulty dial?

**Setup** (`qemcmc/hedgebook.py`, rules fixed before running). 16 natural instruments,
no inverse funds: equity SPY IWM VIXY; rates TLT IEF SHY TIP; credit HYG LQD;
currencies UUP FXY FXE EEM; commodities DBC USO GLD. 56 windows of 252 days, 2012Q1 to
2025Q4. 5 of 16. Primary objective: risk-only on the correlation matrix (most
diversified book; edge-driven, all node weights equal).

## Results

Correlations: median 40% of pairs negative; most negative pair per window median −0.96
(SPY–VIXY; UUP–FXE also near −0.9).

| Objective | Windows > 1 optimum | Windows > 5 | Median optima | Max | Greedy success (median / min) | Distinct optima across windows |
|---|---|---|---|---|---|---|
| Risk-only, correlations (primary) | 18% | 0% | 1 | 3 | 1.00 / 0.44 | 11 |
| Risk-only, covariance | 77% | 0% | 2 | 4 | 0.98 / 0.39 | 6 |
| Mean–variance, λ = 3 | 2% | 0% | 1 | 2 | 1.00 / 0.50 | 44 |

The primary optimum is SPY + VIXY + UUP + FXY + FXE in 36 of 56 windows.

Exact spectral gaps vs single swap (primary objective, T = 0.1 × std(S), 7 windows,
medians): multi-swap 0.36, locally balanced 4.93, quantum best 0.43, quantum
linear-only 0.30. Quantum beats single swap in 0% of windows (it beats multi-swap in 86%).

## Verdict: no

Strong hedges are not enough. Real hedges come in **independent pairs** inside separate
risk factors (equity with volatility, dollar with euro); their benefits simply add, so
the best book is "take the strongest hedge pairs", one peak. The random correlations on
the dial were rugged because their hedges **conflict** (frustration: completing one
hedge breaks another, as in a spin glass). Real markets organise hedges cleanly, so the
frustrated regime did not appear in any real dataset tested (ETFs, stocks, factor
selection, hedge book).
