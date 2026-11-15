# Pilot: market-neutral long–short book (bead b3d, branch `pilot/factor-selection`)

**Idea.** Hold all n assets at equal size, half long and half short, and choose the
split that minimises the book's risk. Positively correlated assets want opposite sides,
which cannot hold for every pair (frustration). Under the market factor this is close
to balanced number partitioning of the betas, a classic rugged problem. Real data, no
synthetic correlations.

**Setup** (`qemcmc/longshort.py`, rules fixed before running). Score S = −sᵀΣs / n²,
s = +1 long, −1 short, real covariance, risk-only. Mirror symmetry broken by fixing
asset 0 long; the state is which n/2 − 1 of the other n − 1 are long (same
count-preserving bit strings and XY circuit). Universes: first 12 / all 16 of the ETF
basket, and 16 large stocks (2 per sector as of 2010). 64 quarterly 252-day windows.
Gaps at T = 0.1 × std(S); multi-swap reported fixed and **tuned per window** (fair
match for the per-window quantum grid).

```bash
python -m qemcmc.longshort         # landscape (both sizes) + gaps at 6 long / 6 short
python -m qemcmc.longshort --big   # gaps at 8 long / 8 short, 2 windows per universe
```

## Landscape: rugged on real data

| Universe | Book | Windows > 1 optimum | Windows > 5 | Median optima | Max | Greedy success (median / min) |
|---|---|---|---|---|---|---|
| ETFs | 6 long / 6 short | 100% | 50% | 5.5 | 10 | 0.33 / 0.11 |
| ETFs | 8 long / 8 short | 100% | **100%** | **13** | 31 | **0.21** / 0.07 |
| Stocks | 6 long / 6 short | 94% | 2% | 2.5 | 6 | 0.55 / 0.21 |
| Stocks | 8 long / 8 short | 100% | 61% | 6 | 12 | 0.36 / 0.13 |

First real-data problem in this project as rugged as the synthetic far end of the dial.

## Mixing: exact spectral gap vs single swap (medians)

| Universe | Book | Windows | Multi-swap (fixed / tuned) | Locally balanced | Quantum (best) | Quantum > swap | Quantum > tuned multi-swap |
|---|---|---|---|---|---|---|---|
| ETFs | 6 / 6 | 64 | 2.25 / 2.34 | 3.35 | 1.56 | 92% | 0% |
| Stocks | 6 / 6 | 64 | 1.20 / 1.32 | 6.36 | 1.26 | 62% | 42% (median quantum ÷ multi 0.92) |
| ETFs | 8 / 8 | 2 | 2.05 / 2.07 | 3.29 | 1.51 | 100% | 0% |
| Stocks | 8 / 8 | 2 | 2.16 / 2.16 | 5.26 | 1.52 | 100% | 50% |

Linear-only phase (hardware-friendly): 1.34 on ETFs, 0.82 on stocks at 6 / 6.

## Conclusions

1. **Real data can be rugged.** The long–short book turns the market factor from the
   cause of easy landscapes into the cause of hard ones.
2. **The quantum proposal beats single-swap Metropolis here on real data** (1.26–1.56×
   at 6 / 6, all windows at 8 / 8). First real-data result in its favour.
3. **It does not beat the stronger classical proposals.** Tuned multi-swap wins on ETFs
   in every window and roughly ties on stocks (quantum wins 42% of windows). Locally
   balanced informed swaps lead everywhere per attempt (3.3–7.3×), though they cost
   k(n−k) score evaluations per attempt.
4. **The hardware-friendly linear-only circuit loses much of the edge** (0.82× on
   stocks), because the hardness lives in the pair (covariance) terms.

**Caveats.** 8 / 8 uses only 2 windows per universe; the quantum grid is small and
tuned per window; temperature fixed at 0.1 × std(S); per-attempt comparison only (no
shot or runtime costs).
