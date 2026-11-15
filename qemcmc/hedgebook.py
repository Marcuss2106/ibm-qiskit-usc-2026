"""Pilot: multi-factor hedge book (bead xyi). Universe and rules fixed before running.

16 natural instruments (no inverse funds) across five risk factors:
    equity SPY IWM VIXY | rates TLT IEF SHY TIP | credit HYG LQD |
    currencies UUP FXY FXE EEM | commodities DBC USO GLD
252-day windows ending each quarter 2012Q1-2025Q4 (VIXY starts January 2011).

Objectives, 5 of 16:
    corr_risk   S = -x'Cx / k^2 on the correlation matrix (primary: most diversified
                book, every position at equal risk, so the landscape is edge-driven)
    cov_risk    S = -x'Sigma x / k^2
    mv_lam3     mean-variance, lam = 3

Usage:
    python -m qemcmc.hedgebook             # landscape for all objectives + gaps
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.circuits import score_terms
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import RESULTS_DIR, enumerate_scores
from qemcmc.subspace import (
    _space,
    chain_gap,
    informed_matrix,
    mixer_matrix,
    multiswap_table,
    proposal_table_fast,
    spectral_gap,
    swap_table,
)

FACTORS = {
    "equity": ["SPY", "IWM", "VIXY"],
    "rates": ["TLT", "IEF", "SHY", "TIP"],
    "credit": ["HYG", "LQD"],
    "currencies": ["UUP", "FXY", "FXE", "EEM"],
    "commodities": ["DBC", "USO", "GLD"],
}
TICKERS = [t for ts in FACTORS.values() for t in ts]
PRICES_CSV = data.DATA_DIR / "hedgebook_prices.csv"
N, K = 16, 5


def corr_of(sigma: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.diag(sigma))
    return sigma / np.outer(d, d)


def load_windows(refresh: bool = False):
    if refresh or not PRICES_CSV.exists():
        data.download_prices(TICKERS, start="2010-12-01").to_csv(PRICES_CSV, float_format="%.6f")
    p = pd.read_csv(PRICES_CSV, index_col="date", parse_dates=True)[TICKERS]
    r = data.daily_returns(data.clean_prices(p.loc["2011-01-04":]))
    return data.window_estimates(r, ends=data.quarter_ends("2012-03-31", "2025-12-31"))


def objective(name: str, mu, sigma):
    """(mu, Sigma, lam) to feed enumerate_scores / score_terms."""
    if name == "corr_risk":
        return np.zeros(N), corr_of(sigma), 1.0
    if name == "cov_risk":
        return np.zeros(N), sigma, 1.0
    if name == "mv_lam3":
        return mu, sigma, 3.0
    raise ValueError(name)


def landscape(dates, mus, sigmas, objectives=("corr_risk", "cov_risk", "mv_lam3")):
    space = _space(N, K)
    nbrs = space.swap_neighbors()
    iu = np.triu_indices(N, 1)
    rows = []
    for w, d in enumerate(dates):
        C = corr_of(sigmas[w])[iu]
        for obj in objectives:
            m, s, lam = objective(obj, mus[w], sigmas[w])
            S = enumerate_scores(space, m, s, lam)
            ends = greedy_endpoints(S, nbrs)
            best = int(S.argmax())
            rows.append({
                "window_end": d.strftime("%Y-%m-%d"), "objective": obj,
                "n_local_opt": int(local_optima(S, nbrs).sum()),
                "greedy_success": float((ends == best).mean()),
                "best": "+".join(TICKERS[i] for i in space.combos[best]),
                "neg_pairs": float((C < 0).mean()), "min_corr": float(C.min()),
            })
    return pd.DataFrame(rows)


def gaps(dates, mus, sigmas, windows, objective_name="corr_risk", tau=0.1,
         betas=(1.0,), gs=(1.0, 3.0), phases=("linear", "full")):
    space = _space(N, K)
    Qswap, Qmulti = swap_table(space), multiswap_table(space)
    A = {b: mixer_matrix(N, K, b, "ring") for b in betas}
    rows = []
    for w in windows:
        m, s, lam = objective(objective_name, mus[w], sigmas[w])
        S = enumerate_scores(space, m, s, lam)
        T = tau * S.std()
        h, J = score_terms(m, s, lam, K)
        g_swap = spectral_gap(Qswap, S, T)
        q = {(b, g, ph): spectral_gap(proposal_table_fast(N, K, h, J, b, g / S.std(), "ring", ph, A=A[b]), S, T)
             for b in betas for g in gs for ph in phases}
        best = max(q, key=q.get)
        rows.append({
            "window_end": dates[w].strftime("%Y-%m-%d"), "objective": objective_name, "tau": tau,
            "multi_ratio": spectral_gap(Qmulti, S, T) / g_swap,
            "balanced_ratio": chain_gap(informed_matrix(space, S, T), S, T) / g_swap,
            "quantum_best_ratio": q[best] / g_swap,
            "quantum_linear_ratio": max(v for k_, v in q.items() if k_[2] == "linear") / g_swap,
            "quantum_best_cfg": f"beta={best[0]},g={best[1]},{best[2]}",
        })
    return pd.DataFrame(rows)


def main() -> None:
    t = time.time()
    dates, mus, sigmas = load_windows()
    land = landscape(dates, mus, sigmas)
    land.to_csv(RESULTS_DIR / "hedgebook_landscape.csv", index=False)
    g = land.groupby("objective", sort=False)
    print(f"Hedge book, 5 of 16, {len(dates)} windows ({dates[0].date()} to {dates[-1].date()})")
    print(f"negative pairs (median): {land.neg_pairs.median():.0%}   most negative corr (median): {land.min_corr.median():+.2f}")
    print(pd.DataFrame({
        "windows>1 opt": g.n_local_opt.apply(lambda x: (x > 1).mean()),
        "windows>5 opt": g.n_local_opt.apply(lambda x: (x > 5).mean()),
        "median opt": g.n_local_opt.median(), "max opt": g.n_local_opt.max(),
        "greedy median": g.greedy_success.median(), "greedy min": g.greedy_success.min(),
        "distinct optima": g.best.nunique(),
    }).round(2).to_string())
    corr = land[land.objective == "corr_risk"]
    print("\nMost common corr_risk optima:", corr.best.value_counts().head(3).to_dict())
    gp = gaps(dates, mus, sigmas, range(0, len(dates), 8))
    gp.to_csv(RESULTS_DIR / "hedgebook_gaps.csv", index=False)
    print(f"\nGaps vs single swap (corr_risk, T = 0.1 x std(S), {len(gp)} windows): medians")
    print(gp[["multi_ratio", "balanced_ratio", "quantum_best_ratio", "quantum_linear_ratio"]].median().round(2).to_string())
    print(f"quantum > swap in {(gp.quantum_best_ratio > 1).mean():.0%} of windows; "
          f"quantum > multi-swap in {(gp.quantum_best_ratio > gp.multi_ratio).mean():.0%}")
    print(f"({time.time() - t:.0f}s)")


if __name__ == "__main__":
    main()
