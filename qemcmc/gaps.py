"""Exact spectral gaps per proposal method (DEVELOPMENT.md §8.3).

Larger gap = faster mixing. All methods share the window, lam and temperature.
Scales are per window, with sigma_S = std of S over valid portfolios:
phase angle gamma = g / sigma_S and temperature T = tau * sigma_S.

Usage:
    python -m qemcmc.gaps --n 12 --k 4                  # full sweep, every 8th window
    python -m qemcmc.gaps --n 16 --k 5 --beta 0.5 --g 1  # chosen settings only
"""

from __future__ import annotations

import argparse
import itertools
import time

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.circuits import score_terms
from qemcmc.objective import RESULTS_DIR, enumerate_scores
from qemcmc.subspace import _space, mixer_matrix, proposal_table_fast, spectral_gap, swap_table

PHASES = ["none", "linear", "ring", "full"]


def run(n, k, windows, lams, betas, gs, taus, phases=PHASES, mixer="ring"):
    space = _space(n, k)
    inst = data.load_instances(n)
    Qswap = swap_table(space)
    A = {b: mixer_matrix(n, k, b, mixer) for b in betas}
    rows = []
    for w, lam in itertools.product(windows, lams):
        mu, sigma = inst["mu"][w], inst["Sigma"][w]
        S = enumerate_scores(space, mu, sigma, lam)
        sd = S.std()
        h, J = score_terms(mu, sigma, lam, k)
        for tau in taus:
            T = tau * sd
            base = {"window_end": inst["dates"][w].strftime("%Y-%m-%d"), "lam": lam, "tau": tau}
            rows.append(base | {"method": "swap", "beta": np.nan, "g": np.nan,
                                "gap": spectral_gap(Qswap, S, T)})
            for phase, b, g in itertools.product(phases, betas, gs):
                if phase == "none" and g != gs[0]:
                    continue  # gamma irrelevant without a phase
                Q = proposal_table_fast(n, k, h, J, b, g / sd, mixer, phase, A=A[b])
                rows.append(base | {"method": f"xy+{phase}", "beta": b, "g": g,
                                    "gap": spectral_gap(Q, S, T)})
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """Median gap ratio vs swap per (lam, tau, method, beta, g), best first."""
    swap = df[df.method == "swap"].set_index(["window_end", "lam", "tau"])["gap"]
    q = df[df.method != "swap"].copy()
    q["ratio"] = q["gap"].to_numpy() / swap.loc[list(zip(q.window_end, q.lam, q.tau))].to_numpy()
    out = q.groupby(["lam", "tau", "method", "beta", "g"])["ratio"].agg(["median", "min", "max"])
    return out.sort_values("median", ascending=False)


def main() -> None:
    p = argparse.ArgumentParser(description="Exact spectral gaps per proposal method.")
    p.add_argument("--n", type=int, default=12)
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--every", type=int, default=8, help="use every Nth window")
    p.add_argument("--lam", type=float, nargs="+", default=[3.0, 30.0])
    p.add_argument("--beta", type=float, nargs="+", default=[0.25, 0.5, 0.785, 1.2])
    p.add_argument("--g", type=float, nargs="+", default=[0.3, 1.0, 3.0])
    p.add_argument("--tau", type=float, nargs="+", default=[0.1, 0.3])
    p.add_argument("--phase", nargs="+", default=PHASES)
    a = p.parse_args()
    t = time.time()
    df = run(a.n, a.k, range(0, 64, a.every), a.lam, a.beta, a.g, a.tau, a.phase)
    out = RESULTS_DIR / f"gaps_n{a.n}_k{a.k}.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} gaps in {time.time() - t:.0f}s -> {out.relative_to(data.ROOT)}")
    s = summary(df)
    with pd.option_context("display.width", 160):
        for (lam, tau), g in s.groupby(level=["lam", "tau"]):
            print(f"\nlam={lam:g}, T={tau:g} x std(S): gap ratio vs swap (median over windows), top 6")
            print(g.head(6).round(2).to_string())


if __name__ == "__main__":
    main()
