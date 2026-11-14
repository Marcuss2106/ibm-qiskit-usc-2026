"""Mean-variance score and the enumeration answer key (DEVELOPMENT.md §3, §6).

    S(x) = mu.x / k - lam / k^2 * x' Sigma x,   sum(x) = k,   maximize.

Usage:

    python -m qemcmc.objective                # default sizes and lam grid
    python -m qemcmc.objective --lam 1 3 10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.states import StateSpace

SIZES = [(8, 3), (12, 4), (16, 5), (20, 6)]  # (n, k)
LAMS = [1.0, 3.0, 10.0]
TIE_TOL = 1e-10
RESULTS_DIR = data.ROOT / "results"


def score(x, mu, Sigma, lam: float, k: int) -> np.ndarray:
    """S(x) for one portfolio x[n] or a batch x[..., n] of 0/1 vectors."""
    x = np.asarray(x, dtype=float)
    ret = x @ mu / k
    var = np.einsum("...i,ij,...j->...", x, Sigma, x)
    return ret - lam / k**2 * var


def enumerate_scores(space: StateSpace, mu, Sigma, lam: float) -> np.ndarray:
    """S for every valid portfolio, indexed by rank. Shape [C]."""
    b = space.bits.astype(float)
    k = space.k
    return b @ mu / k - lam / k**2 * ((b @ Sigma) * b).sum(axis=1)


def summarize(scores: np.ndarray, tol: float = TIE_TOL) -> dict:
    """Optimum, number of states tied with it, and gap to the next-best score."""
    best = int(np.argmax(scores))
    s_star = float(scores[best])
    tied = scores >= s_star - tol
    rest = scores[~tied]
    return {
        "s_star": s_star,
        "best_rank": best,
        "n_ties": int(tied.sum()),
        "second_gap": float(s_star - rest.max()) if rest.size else 0.0,
    }


def answer_key(n: int, k: int, lams=LAMS, instances: dict | None = None) -> pd.DataFrame:
    """One row per (window, lam) with S* and the optimal portfolio."""
    inst = data.load_instances(n) if instances is None else instances
    space = StateSpace(n, k)
    rows = []
    for w, date in enumerate(inst["dates"]):
        mu, sigma = inst["mu"][w], inst["Sigma"][w]
        for lam in lams:
            s = summarize(enumerate_scores(space, mu, sigma, lam))
            r = s["best_rank"]
            rows.append(
                {
                    "window_end": date.strftime("%Y-%m-%d"),
                    "n": n,
                    "k": k,
                    "lam": lam,
                    **s,
                    "best_int": int(space.ints[r]),
                    "best_bitstring": space.bitstring(r),
                    "best_tickers": "+".join(inst["tickers"][i] for i in space.combos[r]),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Enumeration answer key per window.")
    p.add_argument("--lam", type=float, nargs="+", default=LAMS)
    args = p.parse_args()
    RESULTS_DIR.mkdir(exist_ok=True)
    for n, k in SIZES:
        df = answer_key(n, k, args.lam)
        out = RESULTS_DIR / f"answer_key_n{n}_k{k}.csv"
        df.to_csv(out, index=False)
        print(f"\n{k} of {n}: {StateSpace(n, k).size} portfolios -> {out.relative_to(data.ROOT)}")
        g = df.groupby("lam")
        print(
            pd.DataFrame(
                {
                    "windows": g.size(),
                    "unique_opt": g["n_ties"].apply(lambda t: int((t == 1).sum())),
                    "distinct_optima": g["best_int"].nunique(),
                    "median_2nd_gap": g["second_gap"].median(),
                }
            ).to_string()
        )


if __name__ == "__main__":
    main()
