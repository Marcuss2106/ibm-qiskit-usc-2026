"""Pilot: market-neutral long-short book (bead b3d).

Hold all n assets at equal size, half long (s = +1) and half short (s = -1). Score =
minus the book's risk, S = -s' Sigma s / n^2. Positively correlated assets want
opposite sides, which cannot hold for every pair (frustration); under one market
factor this is close to balanced number partitioning of the betas.

Mirror symmetry (s -> -s gives the same risk) is broken by fixing asset 0 long. The
state is which n/2 - 1 of the other n - 1 assets are long: bit x_i = 1 means long, a
fixed-count bit string, so StateSpace, swaps and the count-preserving circuit apply
unchanged (one swap = move one long to short and one short to long).

Usage:
    python -m qemcmc.longshort
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import RESULTS_DIR
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

STOCKS = ["AAPL", "MSFT", "XOM", "CVX", "JPM", "WFC", "JNJ", "PFE",
          "WMT", "PG", "GE", "UPS", "T", "VZ", "MCD", "AMZN"]
STOCK_CSV = data.DATA_DIR / "stock_prices.csv"  # git-ignored cache


def book_signs(space) -> np.ndarray:
    """s for every state: asset 0 long, then +1/-1 from the bits. Shape [C, n]."""
    s = 2 * space.bits.astype(float) - 1
    return np.column_stack([np.ones(space.size), s])


def longshort_scores(space, sigma: np.ndarray) -> np.ndarray:
    n = sigma.shape[0]
    s = book_signs(space)
    return -((s @ sigma) * s).sum(axis=1) / n**2


def longshort_terms(sigma: np.ndarray):
    """h[n-1], J[n-1, n-1] with S(x) = h.x + sum_{i<j} J_ij x_i x_j + const."""
    n = sigma.shape[0]
    a, B = sigma[0, 1:], sigma[1:, 1:]
    linear = 4 * a - 4 * B.sum(axis=1) + 4 * np.diag(B)
    h = -linear / n**2
    J = -8 * B / n**2
    np.fill_diagonal(J, 0.0)
    return h, J


def stock_windows():
    if not STOCK_CSV.exists():
        data.download_prices(STOCKS).to_csv(STOCK_CSV, float_format="%.6f")
    p = pd.read_csv(STOCK_CSV, index_col="date", parse_dates=True)[STOCKS]
    _, _, S = data.window_estimates(data.daily_returns(data.clean_prices(p)))
    return S


def landscape(sigmas, n: int):
    space = _space(n - 1, n // 2 - 1)
    nbrs = space.swap_neighbors()
    rows = []
    for w, sig in enumerate(sigmas):
        S = longshort_scores(space, sig[:n, :n])
        ends = greedy_endpoints(S, nbrs)
        n_opt = int(local_optima(S, nbrs).sum())
        rows.append({"w": w, "n_local_opt": n_opt,
                     "greedy_success": float((ends == S.argmax()).mean()),
                     "best_gap_rel": float((S.max() - np.sort(S)[-2]) / S.std())})
    return pd.DataFrame(rows)


def gaps(sigmas, n: int, windows, tau=0.1, betas=(0.5, 1.0), gs=(1.0, 3.0), phases=("linear", "full"),
         multi_ms=None):
    """Gap ratios vs single swap. Multi-swap is reported fixed (jumps up to k) and tuned
    (best maximum jump size in multi_ms per window), matching the per-window tuning
    the quantum proposal gets."""
    space = _space(n - 1, n // 2 - 1)
    kk = n // 2 - 1
    multi_ms = tuple(range(2, kk + 1)) if multi_ms is None else multi_ms
    Qswap = swap_table(space)
    Qm = {m: multiswap_table(space, m) for m in set(multi_ms) | {kk}}
    A = {b: mixer_matrix(n - 1, n // 2 - 1, b, "ring") for b in betas}
    rows = []
    for w in windows:
        sig = sigmas[w][:n, :n]
        S = longshort_scores(space, sig)
        T = tau * S.std()
        h, J = longshort_terms(sig)
        g_swap = spectral_gap(Qswap, S, T)
        q = {(b, g, ph): spectral_gap(
                proposal_table_fast(n - 1, n // 2 - 1, h, J, b, g / S.std(), "ring", ph, A=A[b]), S, T)
             for b in betas for g in gs for ph in phases}
        best = max(q, key=q.get)
        mg = {m: spectral_gap(Qm[m], S, T) for m in Qm}
        rows.append({"w": w,
                     "multi_ratio": mg[kk] / g_swap,
                     "multi_tuned_ratio": max(mg[m] for m in multi_ms) / g_swap,
                     "balanced_ratio": chain_gap(informed_matrix(space, S, T), S, T) / g_swap,
                     "quantum_best_ratio": q[best] / g_swap,
                     "quantum_linear_ratio": max((v for k_, v in q.items() if k_[2] == "linear"),
                                                 default=np.nan) / g_swap,
                     "quantum_cfg": f"beta={best[0]},g={best[1]},{best[2]}"})
    return pd.DataFrame(rows)


def show_landscape(name, df):
    print(f"  {name:22s} >1 opt {(df.n_local_opt > 1).mean():4.0%}  >5 opt {(df.n_local_opt > 5).mean():4.0%}  "
          f"median opt {df.n_local_opt.median():5.1f}  max {df.n_local_opt.max():3d}  "
          f"greedy median {df.greedy_success.median():.2f}  min {df.greedy_success.min():.2f}")


def show_gaps(name, df):
    m = df[["multi_ratio", "multi_tuned_ratio", "balanced_ratio", "quantum_best_ratio",
            "quantum_linear_ratio"]].median()
    print(f"  {name:8s} multi {m.multi_ratio:.2f} (tuned {m.multi_tuned_ratio:.2f})  "
          f"balanced {m.balanced_ratio:.2f}  quantum {m.quantum_best_ratio:.2f} "
          f"(linear {m.quantum_linear_ratio:.2f})  quantum>swap {(df.quantum_best_ratio > 1).mean():.0%}  "
          f"quantum>tuned multi {(df.quantum_best_ratio > df.multi_tuned_ratio).mean():.0%}  "
          f"[{len(df)} windows]")


def main_big() -> None:
    """8 long / 8 short gaps on a few windows (6,435 states: about a minute per gap)."""
    t = time.time()
    universes = {"ETFs": data.load_instances(20)["Sigma"], "stocks": stock_windows()}
    rows = []
    print("Exact gaps vs single swap, 8 long / 8 short (n = 16), T = 0.1 x std(S), full phase:")
    for uname, sig in universes.items():
        df = gaps(sig, 16, [0, 32], betas=(0.5, 1.0), gs=(3.0,), phases=("full",),
                  multi_ms=(2, 4, 7)).assign(universe=uname, n=16)
        rows.append(df)
        show_gaps(uname, df)
        print(df[["w", "multi_ratio", "multi_tuned_ratio", "balanced_ratio", "quantum_best_ratio",
                  "quantum_cfg"]].round(2).to_string(index=False))
    pd.concat(rows).to_csv(RESULTS_DIR / "longshort_gaps_n16.csv", index=False)
    print(f"({time.time() - t:.0f}s)")


def main() -> None:
    import sys

    if "--big" in sys.argv:
        return main_big()
    t = time.time()
    universes = {"ETFs": data.load_instances(20)["Sigma"], "stocks": stock_windows()}
    allrows = []
    print("Landscape (64 windows):")
    for uname, sig in universes.items():
        for n in (12, 16):
            df = landscape(sig, n).assign(universe=uname, n=n)
            allrows.append(df)
            show_landscape(f"{uname} {n // 2} long/{n // 2} short", df)
    pd.concat(allrows).to_csv(RESULTS_DIR / "longshort_landscape.csv", index=False)
    print("\nExact gaps vs single swap, 6 long / 6 short (n = 12), T = 0.1 x std(S):")
    grows = []
    for uname, sig in universes.items():
        df = gaps(sig, 12, range(64)).assign(universe=uname, n=12)
        grows.append(df)
        show_gaps(uname, df)
    pd.concat(grows).to_csv(RESULTS_DIR / "longshort_gaps_n12.csv", index=False)
    print(f"({time.time() - t:.0f}s)")


if __name__ == "__main__":
    main()
