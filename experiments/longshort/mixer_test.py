"""Does a better mixer let the quantum proposal beat multi-swap on the long-short book?

Variants of the palindromic circuit (full score phase), 6 long / 6 short, all 64
windows, ETFs and stocks:
    ring     XY gates on a ring in basket order (the earlier result)
    complete XY gates between every pair (any two assets can swap)
    ordered  ring ordered so the most strongly coupled pairs (largest |J|) are adjacent
Each variant gets its best (beta, g) per window from the same grid; multi-swap gets its
best maximum jump size per window. Also reports mean proposal jump distance (swaps).

Run from the repo root:
    PYTHONPATH=. python experiments/longshort/mixer_test.py
"""
import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.longshort import longshort_scores, longshort_terms, stock_windows
from qemcmc.subspace import (
    _space, chain_gap, informed_matrix, mixer_matrix, multiswap_table,
    proposal_table_fast, spectral_gap, swap_table,
)

N = 12
NV, KV = N - 1, N // 2 - 1  # 11 free assets, 5 more longs
BETAS = (0.1, 0.2, 0.3, 0.5, 0.75, 1.0)
GS = (1.0, 3.0)
TAU = 0.1


def coupling_order(J: np.ndarray) -> list[int]:
    """Greedy max-weight chain: start at the most coupled asset, always step to the
    unvisited asset with the largest |J| to the current one."""
    A = np.abs(J + J.T)
    order = [int(A.sum(1).argmax())]
    left = set(range(len(A))) - set(order)
    while left:
        nxt = max(left, key=lambda j: A[order[-1], j])
        order.append(nxt)
        left.remove(nxt)
    return order


def mean_jump(Q: np.ndarray, dist: np.ndarray) -> float:
    return float((Q * dist).sum(axis=1).mean())


def run(name, sigmas):
    sp = _space(NV, KV)
    b = sp.bits.astype(np.int32)
    dist = KV - b @ b.T
    Qswap = swap_table(sp)
    Qm = {m: multiswap_table(sp, m) for m in range(2, KV + 1)}
    A_fixed = {(mx, be): mixer_matrix(NV, KV, be, mx) for mx in ("ring", "complete") for be in BETAS}
    rows = []
    for w in range(64):
        sig = sigmas[w][:N, :N]
        S = longshort_scores(sp, sig)
        T = TAU * S.std()
        h, J = longshort_terms(sig)
        g_swap = spectral_gap(Qswap, S, T)
        mg = {m: spectral_gap(Qm[m], S, T) for m in Qm}
        m_best = max(mg, key=mg.get)
        row = {"universe": name, "w": w,
               "multi_tuned": mg[m_best] / g_swap, "multi_jump": mean_jump(Qm[m_best], dist),
               "balanced": chain_gap(informed_matrix(sp, S, T), S, T) / g_swap}
        order = coupling_order(J)
        for variant in ("ring", "complete", "ordered"):
            best, best_Q, best_cfg = 0.0, None, None
            for be in BETAS:
                if variant == "ordered":
                    A, mx, od = mixer_matrix(NV, KV, be, "ring", order), "ring", order
                else:
                    A, mx, od = A_fixed[(variant, be)], variant, None
                for g in GS:
                    Q = proposal_table_fast(NV, KV, h, J, be, g / S.std(), mx, "full", order=od, A=A)
                    r = spectral_gap(Q, S, T) / g_swap
                    if r > best:
                        best, best_Q, best_cfg = r, Q, (be, g)
            row |= {variant: best, f"{variant}_jump": mean_jump(best_Q, dist),
                    f"{variant}_beta": best_cfg[0]}
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = pd.concat([run("ETFs", data.load_instances(20)["Sigma"]), run("stocks", stock_windows())])
    out.to_csv(data.ROOT / "results" / "longshort_mixers_n12.csv", index=False)
    for name, d in out.groupby("universe", sort=False):
        print(f"\n== {name}, 6 long / 6 short, 64 windows: gap vs single swap (median) | mean jump (swaps)")
        print(f"  tuned multi-swap  {d.multi_tuned.median():.2f} | {d.multi_jump.median():.2f}")
        print(f"  locally balanced  {d.balanced.median():.2f} | 1.00")
        for v in ("ring", "complete", "ordered"):
            print(f"  quantum {v:9s} {d[v].median():.2f} | {d[v + '_jump'].median():.2f}   "
                  f"beats tuned multi in {(d[v] > d.multi_tuned).mean():.0%}   "
                  f"median beta {d[v + '_beta'].median():.2f}")
