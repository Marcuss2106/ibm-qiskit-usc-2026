"""Is the poor quantum gap ratio caused by the first-order phase approximation?

Fit the best pairwise (quadratic) phase to the exact log posterior by least squares
over all subsets, then recompute the quantum/swap spectral-gap ratio at T = 1.
5 of 14 non-equity factors, every 8th window. Run from the repo root:
    PYTHONPATH=. python experiments/factor_pilot/fitted_phase.py
"""
import numpy as np
import pandas as pd

from qemcmc import factors as F
from qemcmc.states import StateSpace
from qemcmc.subspace import mixer_matrix, proposal_table_fast, spectral_gap, swap_table

n, k = 14, 5
sp = StateSpace(n, k)
x = sp.bits.astype(float)
iu = np.triu_indices(n, 1)
X = np.column_stack([x, x[:, iu[0]] * x[:, iu[1]]])
dates, cs, Rs = F.window_correlations(F.load_factor_data(), F.FACTORS[:n])
Qswap = swap_table(sp)
A = {b: mixer_matrix(n, k, b, "ring") for b in (0.3, 0.5, 1.0)}

for w in range(0, 64, 8):
    S = F.log_posterior(F.r2_all(sp, cs[w], Rs[w]))
    coef, *_ = np.linalg.lstsq(X, S - S.mean(), rcond=None)
    h = coef[:n]
    J = np.zeros((n, n))
    J[iu] = coef[n:]
    rank_corr = pd.Series(X @ coef).corr(pd.Series(S), method="spearman")
    g_swap = spectral_gap(Qswap, S, 1.0)
    best = max(
        (spectral_gap(proposal_table_fast(n, k, h, J, b, g, "ring", "full", A=A[b]), S, 1.0) / g_swap, b, g)
        for b in (0.3, 0.5, 1.0)
        for g in (0.3, 1.0, 3.0)
    )
    print(f"{dates[w].date()}  fitted-phase rank corr {rank_corr:.2f}  "
          f"best quantum/swap gap {best[0]:.2f} (beta={best[1]}, gamma={best[2]})")
