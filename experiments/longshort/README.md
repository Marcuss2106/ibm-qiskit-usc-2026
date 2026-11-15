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

## Mixer variants (2026-11-15, `mixer_test.py`, `phase_control.py`)

Question: does the ring mixer's restriction (only ring-adjacent assets swap) explain the
loss to multi-swap? 6 long / 6 short, all 64 windows, full score phase, best (β, g) per
window from β ∈ {0.1, 0.2, 0.3, 0.5, 0.75, 1.0}, g ∈ {1, 3}; multi-swap tuned per window.

| Universe | Tuned multi-swap | Locally balanced | Quantum ring | Quantum **complete** | Quantum ordered ring | Complete beats tuned multi-swap |
|---|---|---|---|---|---|---|
| ETFs | 2.34 (jump 3.0) | 3.35 | 1.77 | **2.68** (jump 2.6) | 2.22 | **89%** of windows |
| Stocks | 1.32 (jump 2.0) | 6.36 | 1.35 | **2.08** (jump 2.5) | 1.89 | **88%** |

(gap vs single swap, medians; "jump" = mean proposal distance in swaps; ordered ring =
assets arranged so the most strongly coupled pairs are adjacent, which beats tuned
multi-swap in 45% / 59% of windows.)

**Control: is it the score phase?** Same complete-mixer circuit with the phase off:
ETFs 1.84, stocks 1.05, below tuned multi-swap (beats it in 0% / 17% of windows). Turning
the phase on improves it in 100% / 98% of windows (median 1.46× / 1.90×). The gain comes
from score information, not from jumping farther: the complete mixer jumps no farther
than multi-swap on ETFs.

**What this does and does not show.**

- First result in this project where the quantum proposal beats a tuned blind long-jump
  baseline on real data, and the gain is attributable to the score phase.
- Locally balanced informed swaps still mix faster per attempt (3.35× / 6.36×), but each
  attempt costs k(n−k) = 30 score evaluations here. Per score evaluation they fall to
  about 0.11× / 0.21× single swap; the quantum proposal uses one score evaluation per
  attempt (plus the circuit).
- The complete mixer needs XY gates between all 55 pairs (twice): fine in simulation,
  but on a heavy-hex device it needs heavy routing. The hardware-friendly ordered ring
  keeps part of the gain (beats tuned multi-swap in 45–59% of windows).
- The quantum side was tuned over 12 settings per window, multi-swap over 4.
- Not yet tested: parallel tempering (recommended baseline in
  `docs/research/rugged-landscapes.md`), 8 long / 8 short, cost per shot or second.
