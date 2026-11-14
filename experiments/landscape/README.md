# Landscape experiments (bead ieo)

Why is the 5-of-16 mean–variance landscape almost always single-peaked under swaps,
and what changes that? One-off scripts; results summarized below and in the `ieo` bead
notes (`bd show ibm-qiskit-usc-2026-ieo`). Run from the repo root after
`python -m qemcmc.data`:

```bash
PYTHONPATH=. python experiments/landscape/why_unimodal.py
PYTHONPATH=. python experiments/landscape/etf_fixes.py
PYTHONPATH=. python experiments/landscape/stock_test.py data/stock_prices.csv   # downloads if missing
PYTHONPATH=. python experiments/landscape/market_factor.py
PYTHONPATH=. python experiments/landscape/residual.py data/stock_prices.csv     # needs stock_test first
PYTHONPATH=. python experiments/landscape/alpha_test.py
```

All use 5 of 16, 64 quarterly windows. "Optima" = local optima under single swaps;
"greedy" = share of starts from which steepest ascent reaches the global optimum.

| Script | Question | Result |
|---|---|---|
| `why_unimodal.py` | Is it the data or the method? | Real Σ, any λ: 1 optimum. Real μ and volatilities with random correlations, risk-only: median 12 optima, greedy 0.19. Adding inverse SPY/TLT: at most 3. |
| `etf_fixes.py` | Do μ shrinkage or shorter windows (252/126/63 days) help? | No. At most 3 optima anywhere; median greedy 1.0 in every setting. |
| `stock_test.py` | Do 16 large stocks (2 per sector, as of 2010) help? | No. At most 5 optima; median greedy 1.0. |
| `market_factor.py` | Is the common market factor the cause? | Yes. Random correlations with a growing market factor: median optima 12, 8, 2, 1. Real ETFs (mean correlation +0.31) sit in the single-peak zone. |
| `residual.py` | Real Σ with the top principal component removed? | Risk-only: 84% of windows with more than 1 optimum, median 3, greedy 0.62 (ETFs; stocks similar). With returns (λ = 3): still 1 optimum. |
| `alpha_test.py` | SPY-hedged alpha vs residual risk; λ sweep | Hedged: single-peaked for λ 1–100. Plain λ = 30: 20% of windows with 2–3 optima, returns still change the optimum in 88%. Greedy ring captures 20–30% of edge weight. |

Status: our own experimental result, not yet checked against the literature (bead
`5xy`). Framing decision in bead `lhr`.
