"""Pilot: Bayesian selection of k factors that explain SPY's daily returns.

State: which k of n candidate factors enter a linear regression for SPY returns
(same bit strings and StateSpace as the portfolio problem). Score: exact log
posterior of the subset under Zellner's g-prior with g = N and a uniform prior over
k-subsets. With k fixed this depends only on the subset's R^2:

    S(x) = -((N - 1) / 2) * log(1 + g * (1 - R^2(x)))     (up to a constant)

T = 1 is the actual posterior, so the sampling temperature is not a tuning choice.
R^2 is not pairwise; the circuit's phase uses the first-order approximation
    R^2(x) ~ sum_i c_i^2 x_i - 2 sum_{i<j} c_i c_j rho_ij x_i x_j
(c = correlation with SPY, rho = factor correlations). Acceptance uses the exact S,
so the approximation affects efficiency only, never correctness.

Usage:
    python -m qemcmc.factors            # landscape + posterior + gaps, both universes
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import RESULTS_DIR
from qemcmc.states import StateSpace
from qemcmc.subspace import mixer_matrix, proposal_table_fast, spectral_gap, swap_table

TARGET = "SPY"
LEVELS = ["^VIX", "^IRX", "^FVX", "^TNX", "^TYX"]  # use daily changes in level
RETURNS = ["HYG", "LQD", "TIP", "UUP", "DBC", "USO", "GLD", "SLV", "FXY"]
EQUITY = ["EFA", "EEM"]  # equity-like; last so the non-equity universe is a prefix
FACTORS = LEVELS + RETURNS + EQUITY  # 16, none are SPY components
PRICES_CSV = data.DATA_DIR / "factor_prices.csv"


def load_factor_data(refresh: bool = False) -> pd.DataFrame:
    """Daily SPY return and factor moves (returns, or level changes for indices)."""
    if refresh or not PRICES_CSV.exists():
        p = data.download_prices([TARGET] + FACTORS)
        p.to_csv(PRICES_CSV, float_format="%.6f")
    p = pd.read_csv(PRICES_CSV, index_col="date", parse_dates=True)
    p = p.sort_index().ffill(limit=data.MAX_FFILL)
    moves = pd.concat(
        [p[[TARGET] + RETURNS + EQUITY].pct_change(), p[LEVELS].diff()], axis=1
    )[[TARGET] + FACTORS]
    return moves.iloc[1:]


def window_correlations(moves: pd.DataFrame, factors, ends=None, window: int = data.WINDOW):
    """Per window: c[W, n] (factor-SPY correlations), R[W, n, n] (factor correlations)."""
    ends = data.quarter_ends() if ends is None else ends
    cs, Rs, dates = [], [], []
    for q in ends:
        w = moves.loc[:q, [TARGET] + list(factors)].iloc[-window:]
        if len(w) < window or w.isna().any().any():
            raise ValueError(f"window ending {q.date()} incomplete")
        C = np.corrcoef(w.to_numpy(), rowvar=False)
        cs.append(C[0, 1:])
        Rs.append(C[1:, 1:])
        dates.append(w.index[-1])
    return pd.DatetimeIndex(dates), np.array(cs), np.array(Rs)


def r2_all(space: StateSpace, c: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Exact R^2 of the OLS regression (with intercept) for every k-subset."""
    idx = space.combos
    Rs = R[idx[:, :, None], idx[:, None, :]]
    cs = c[idx]
    beta = np.linalg.solve(Rs, cs[..., None])[..., 0]
    return (cs * beta).sum(axis=1)


def log_posterior(r2: np.ndarray, N: int = data.WINDOW, g: float | None = None) -> np.ndarray:
    g = float(N) if g is None else g
    return -((N - 1) / 2) * np.log1p(g * (1 - r2))


def pairwise_terms(c, R, r2_ref: float, N: int = data.WINDOW, g: float | None = None):
    """h, J for the circuit phase: first-order R^2 terms scaled to log-posterior units
    by the slope dS/dR^2 at r2_ref."""
    g = float(N) if g is None else g
    slope = ((N - 1) / 2) * g / (1 + g * (1 - r2_ref))
    h = slope * c**2
    J = slope * (-2 * np.outer(c, c) * R)
    np.fill_diagonal(J, 0.0)
    return h, J


def pairwise_r2(space: StateSpace, c, R) -> np.ndarray:
    x = space.bits.astype(float)
    J = -2 * np.outer(c, c) * R
    np.fill_diagonal(J, 0.0)
    return x @ c**2 + 0.5 * np.einsum("si,ij,sj->s", x, J, x)


def posterior_stats(S: np.ndarray, nbrs: np.ndarray) -> dict:
    """Modes and how posterior mass (T = 1) spreads across them."""
    pi = np.exp(S - S.max())
    pi /= pi.sum()
    best = int(np.argmax(S))
    ends = greedy_endpoints(S, nbrs)
    mass_by_mode = pd.Series(pi).groupby(ends).sum()
    n_opt = int(local_optima(S, nbrs).sum())
    return {
        "n_local_opt": n_opt,
        "greedy_success": float((ends == best).mean()),
        "mass_top_state": float(pi[best]),
        "mass_other_modes": float(1 - mass_by_mode.get(best, 0.0)),
        "modes_over_1pct": int((mass_by_mode > 0.01).sum()),
        "eff_states": float(np.exp(-(pi * np.log(pi + 1e-300)).sum())),
    }


def run(n: int, k: int, label: str, gap_every: int = 8, betas=(0.5, 1.0), gs=(3.0,)):
    moves = load_factor_data()
    factors = FACTORS[:n]
    dates, cs, Rs = window_correlations(moves, factors)
    space = StateSpace(n, k)
    nbrs = space.swap_neighbors()
    Qswap = swap_table(space)
    A = {b: mixer_matrix(n, k, b, "ring") for b in betas}
    rows = []
    for w in range(len(dates)):
        r2 = r2_all(space, cs[w], Rs[w])
        S = log_posterior(r2)
        row = {"window_end": dates[w].strftime("%Y-%m-%d"), "universe": label, "n": n, "k": k,
               "r2_best": float(r2.max()),
               "pairwise_rank_corr": float(pd.Series(pairwise_r2(space, cs[w], Rs[w])).corr(
                   pd.Series(r2), method="spearman")),
               "frac_complement_pairs": float(
                   (np.triu(-2 * np.outer(cs[w], cs[w]) * Rs[w], 1) > 0).sum() / (n * (n - 1) / 2))}
        row |= posterior_stats(S, nbrs)
        if w % gap_every == 0:
            g_swap = spectral_gap(Qswap, S, 1.0)
            h, J = pairwise_terms(cs[w], Rs[w], float(np.median(r2)))
            best_ratio, best_cfg = 0.0, ""
            for b in betas:
                for gg in gs:
                    for phase in ("linear", "full"):
                        Q = proposal_table_fast(n, k, h, J, b, gg / S.std(), "ring", phase, A=A[b])
                        ratio = spectral_gap(Q, S, 1.0) / g_swap
                        if ratio > best_ratio:
                            best_ratio, best_cfg = ratio, f"beta={b},g={gg},{phase}"
            row |= {"swap_gap": g_swap, "quantum_gap_ratio": best_ratio, "quantum_cfg": best_cfg}
        rows.append(row)
    return pd.DataFrame(rows)


def report(df: pd.DataFrame) -> None:
    gp = df.dropna(subset=["swap_gap"])
    print(f"\n=== {df.universe.iloc[0]}: {df.k.iloc[0]} of {df.n.iloc[0]} factors, {len(df)} windows ===")
    print(f"best R^2 (median):                       {df.r2_best.median():.2f}")
    print(f"pairwise approx vs exact R^2 (rank corr): {df.pairwise_rank_corr.median():.2f}")
    print(f"complementary pairs (positive edges):    {df.frac_complement_pairs.median():.0%}")
    print(f"windows with >1 local optimum:           {(df.n_local_opt > 1).mean():.0%}  "
          f"(>5: {(df.n_local_opt > 5).mean():.0%}, median {df.n_local_opt.median():.0f}, max {df.n_local_opt.max()})")
    print(f"greedy success (median / min):           {df.greedy_success.median():.2f} / {df.greedy_success.min():.2f}")
    print(f"posterior mass on top subset (median):   {df.mass_top_state.median():.2f}")
    print(f"posterior mass in other modes (median):  {df.mass_other_modes.median():.3f}  "
          f"(windows with >5%: {(df.mass_other_modes > 0.05).mean():.0%})")
    print(f"effective number of subsets (median):    {df.eff_states.median():.1f}")
    print(f"swap-chain spectral gap at T=1 (median): {gp.swap_gap.median():.2e}  ({len(gp)} windows)")
    print(f"quantum/swap gap ratio (median, range):  {gp.quantum_gap_ratio.median():.2f}  "
          f"({gp.quantum_gap_ratio.min():.2f}-{gp.quantum_gap_ratio.max():.2f})")


def main() -> None:
    p = argparse.ArgumentParser(description="Bayesian factor-selection pilot.")
    p.add_argument("--k", type=int, default=5)
    a = p.parse_args()
    t = time.time()
    for n, label in [(14, "non-equity"), (16, "all")]:
        df = run(n, a.k, label)
        df.to_csv(RESULTS_DIR / f"factor_pilot_{label}_n{n}_k{a.k}.csv", index=False)
        report(df)
    print(f"\n({time.time() - t:.0f}s)")


if __name__ == "__main__":
    main()
