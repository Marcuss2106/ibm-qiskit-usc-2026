"""Landscape check (DEVELOPMENT.md §8.1): local optima under the swap neighborhood.

For every window, size and lam, enumerate all valid portfolios and report:

- n_local_opt: portfolios no single swap improves (the global optimum is one).
- group: "1", "2-5" or ">5" local optima.
- greedy_success: fraction of starting portfolios from which steepest-ascent
  swaps end at the global optimum (its basin share). Low = hard for descent.

Usage:

    python -m qemcmc.landscape
    python -m qemcmc.landscape --lam 1 3 10
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.objective import LAMS, RESULTS_DIR, SIZES, TIE_TOL, enumerate_scores
from qemcmc.states import StateSpace

GROUPS = ["1", "2-5", ">5"]


def group_of(count: int) -> str:
    return "1" if count == 1 else "2-5" if count <= 5 else ">5"


def local_optima(scores: np.ndarray, neighbors: np.ndarray, tol: float = TIE_TOL) -> np.ndarray:
    """Boolean mask of states with no strictly better swap neighbor."""
    return scores[neighbors].max(axis=1) <= scores + tol


def greedy_endpoints(scores: np.ndarray, neighbors: np.ndarray, tol: float = TIE_TOL) -> np.ndarray:
    """Rank of the local optimum steepest ascent reaches from each start."""
    best_nbr = neighbors[np.arange(len(scores)), scores[neighbors].argmax(axis=1)]
    step = np.where(scores[best_nbr] > scores + tol, best_nbr, np.arange(len(scores)))
    while True:  # pointer jumping: follow successors until every chain is fixed
        nxt = step[step]
        if np.array_equal(nxt, step):
            return step
        step = nxt


def analyze(scores: np.ndarray, neighbors: np.ndarray) -> dict:
    is_opt = local_optima(scores, neighbors)
    best = int(np.argmax(scores))
    ends = greedy_endpoints(scores, neighbors)
    n_opt = int(is_opt.sum())
    return {
        "n_local_opt": n_opt,
        "group": group_of(n_opt),
        "greedy_success": float((ends == best).mean()),
    }


def landscape(n: int, k: int, lams=LAMS, instances: dict | None = None) -> pd.DataFrame:
    inst = data.load_instances(n) if instances is None else instances
    space = StateSpace(n, k)
    nbrs = space.swap_neighbors()
    rows = []
    for w, date in enumerate(inst["dates"]):
        for lam in lams:
            scores = enumerate_scores(space, inst["mu"][w], inst["Sigma"][w], lam)
            rows.append(
                {"window_end": date.strftime("%Y-%m-%d"), "n": n, "k": k, "lam": lam}
                | analyze(scores, nbrs)
            )
    return pd.DataFrame(rows)


def select_windows(df: pd.DataFrame, lam: float, per_group: int = 5, seed: int = 0) -> pd.DataFrame:
    """Stratified pick for the main experiments: up to per_group windows from
    each local-optimum group, at random with a fixed seed (no hand-picking)."""
    sub = df[df["lam"] == lam]
    picks = [
        g.sample(min(per_group, len(g)), random_state=seed)
        for _, g in sub.groupby("group", sort=False)
    ]
    return pd.concat(picks).sort_values("window_end")


def summary(df: pd.DataFrame) -> pd.DataFrame:
    counts = pd.crosstab(df["lam"], df["group"]).reindex(columns=GROUPS, fill_value=0)
    g = df.groupby("lam")
    counts["median_opt"] = g["n_local_opt"].median()
    counts["max_opt"] = g["n_local_opt"].max()
    counts["median_greedy_success"] = g["greedy_success"].median().round(3)
    return counts


def main() -> None:
    p = argparse.ArgumentParser(description="Swap-neighborhood landscape check.")
    p.add_argument("--lam", type=float, nargs="+", default=LAMS)
    args = p.parse_args()
    RESULTS_DIR.mkdir(exist_ok=True)
    for n, k in SIZES:
        df = landscape(n, k, args.lam)
        out = RESULTS_DIR / f"landscape_n{n}_k{k}.csv"
        df.to_csv(out, index=False)
        print(f"\n{k} of {n} -> {out.relative_to(data.ROOT)}  (windows per group)")
        print(summary(df).to_string())


if __name__ == "__main__":
    main()
