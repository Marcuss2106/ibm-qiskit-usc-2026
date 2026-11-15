"""Difficulty dial (bead t3h): where, if anywhere, does the quantum proposal win?

Each window's real covariance has its market component (top principal component)
partly removed, Sigma(s) = Sigma - s * l1 * v1 v1', s in {0, .25, .5, .75, 1}; a
final "random" point replaces the correlations with a random 3-factor model (real
volatilities, no market factor). Simulation only, full score phase.

Per (window, dial point, objective, temperature): local optima, greedy success, and
exact spectral gaps of swap, multi-swap (global Kawasaki), locally balanced informed
swaps (Zanella 2019; costs k(n-k) score evaluations per step) and the quantum
proposal (best of a small beta/g grid per window, plus one fixed setting). Ratios
are vs. swap, per attempt.

Usage:
    python -m qemcmc.dial --n 12 --k 4 --every 4
    python -m qemcmc.dial --n 16 --k 5 --every 16 --tau 0.1
"""

from __future__ import annotations

import argparse
import itertools
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

DIAL = [0.0, 0.25, 0.5, 0.75, 1.0, "random"]
OBJECTIVES = {"lam30": 30.0, "risk_only": None}
FIXED = (1.0, 3.0, "full")  # beta, g, phase for the fixed quantum setting


def dial_sigma(sigma: np.ndarray, s, rng: np.random.Generator) -> np.ndarray:
    if s == "random":
        n = len(sigma)
        vol = np.sqrt(np.diag(sigma))
        A = rng.normal(size=(n, 3))
        C = A @ A.T + np.diag(rng.uniform(0.1, 0.5, n))
        d = np.sqrt(np.diag(C))
        return C / np.outer(d, d) * np.outer(vol, vol)
    w, v = np.linalg.eigh(sigma)
    return sigma - s * w[-1] * np.outer(v[:, -1], v[:, -1])


def run(n, k, windows, taus, betas, gs, phases=("linear", "full"), seed=0, dial=DIAL):
    space = _space(n, k)
    nbrs = space.swap_neighbors()
    Qswap, Qmulti = swap_table(space), multiswap_table(space)
    A = {b: mixer_matrix(n, k, b, "ring") for b in set(betas) | {FIXED[0]}}
    inst = data.load_instances(n)
    rng = np.random.default_rng(seed)
    rows = []
    for w in windows:
        mu, sig0 = inst["mu"][w], inst["Sigma"][w]
        for s in dial:
            sig = dial_sigma(sig0, s, rng)
            for obj, lam in OBJECTIVES.items():
                m, l = (mu, lam) if lam is not None else (np.zeros(n), 1.0)
                S = enumerate_scores(space, m, sig, l)
                sd = S.std()
                h, J = score_terms(m, sig, l, k)
                ends = greedy_endpoints(S, nbrs)
                base = {
                    "window_end": inst["dates"][w].strftime("%Y-%m-%d"), "dial": str(s),
                    "objective": obj, "n_local_opt": int(local_optima(S, nbrs).sum()),
                    "greedy_success": float((ends == S.argmax()).mean()),
                }
                for tau in taus:
                    T = tau * sd
                    g_swap = spectral_gap(Qswap, S, T)
                    qs = {}
                    for b, g, ph in itertools.product(betas, gs, phases):
                        Q = proposal_table_fast(n, k, h, J, b, g / sd, "ring", ph, A=A[b])
                        qs[(b, g, ph)] = spectral_gap(Q, S, T)
                    if FIXED not in qs:
                        Q = proposal_table_fast(n, k, h, J, FIXED[0], FIXED[1] / sd, "ring", FIXED[2], A=A[FIXED[0]])
                        qs[FIXED] = spectral_gap(Q, S, T)
                    best = max(qs, key=qs.get)
                    rows.append(base | {
                        "tau": tau, "swap_gap": g_swap,
                        "multi_ratio": spectral_gap(Qmulti, S, T) / g_swap,
                        "balanced_ratio": chain_gap(informed_matrix(space, S, T), S, T) / g_swap,
                        "quantum_best_ratio": qs[best] / g_swap,
                        "quantum_best_cfg": f"beta={best[0]},g={best[1]},{best[2]}",
                        "quantum_fixed_ratio": qs[FIXED] / g_swap,
                    })
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["objective", "tau", "dial"], sort=False)
    out = pd.DataFrame({
        "local_opt": g["n_local_opt"].median(),
        "greedy": g["greedy_success"].median(),
        "multi/swap": g["multi_ratio"].median(),
        "balanced/swap": g["balanced_ratio"].median(),
        "quantum_fixed/swap": g["quantum_fixed_ratio"].median(),
        "quantum_best/swap": g["quantum_best_ratio"].median(),
        "quantum_best>1": g["quantum_best_ratio"].apply(lambda r: (r > 1).mean()),
        "quantum>multi": g.apply(lambda d: (d.quantum_best_ratio > d.multi_ratio).mean(), include_groups=False),
    })
    return out.round(2)


def main() -> None:
    p = argparse.ArgumentParser(description="Difficulty dial experiment.")
    p.add_argument("--n", type=int, default=12)
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--every", type=int, default=4)
    p.add_argument("--tau", type=float, nargs="+", default=[0.1, 0.3])
    p.add_argument("--beta", type=float, nargs="+", default=[0.5, 1.0])
    p.add_argument("--g", type=float, nargs="+", default=[1.0, 3.0])
    p.add_argument("--phase", nargs="+", default=["linear", "full"])
    p.add_argument("--dial", nargs="+", default=[str(s) for s in DIAL])
    a = p.parse_args()
    dial = [s if s == "random" else float(s) for s in a.dial]
    t = time.time()
    df = run(a.n, a.k, range(0, 64, a.every), a.tau, a.beta, a.g, tuple(a.phase), dial=dial)
    out = RESULTS_DIR / f"dial_n{a.n}_k{a.k}.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} rows in {time.time() - t:.0f}s -> {out.relative_to(data.ROOT)}")
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(summary(df).to_string())


if __name__ == "__main__":
    main()
