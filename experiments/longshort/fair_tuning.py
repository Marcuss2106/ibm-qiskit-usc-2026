"""Equal tuning effort: one setting per method, chosen on train windows, tested fixed.

6 long / 6 short, ETFs and stocks. Train = even windows, test = odd windows. Each
method's single setting maximises its median gap ratio (vs single swap) on train; the
test table uses that setting unchanged. Removes the per-window optimism of the earlier
runs on both sides. Includes the hardware-cheap circuits.

Run from the repo root:
    PYTHONPATH=. python experiments/longshort/fair_tuning.py
"""
import itertools

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.longshort import longshort_scores, longshort_terms, stock_windows
from qemcmc.subspace import (
    _space, chain_gap, informed_matrix, mixer_matrix, multiswap_table,
    proposal_table_fast, spectral_gap, swap_table,
)

N, NV, KV, TAU = 12, 11, 5, 0.1
BETAS = (0.1, 0.2, 0.3, 0.5, 0.75, 1.0)
GS = (1.0, 3.0)
VARIANTS = {  # name: (mixer, phase, ordered)
    "complete+full": ("complete", "full", False),
    "ring+full": ("ring", "full", False),
    "ordered ring+full": ("ring", "full", True),
    "ordered ring+ring phase (hw)": ("ring", "ring", True),
    "ring+linear (hw target)": ("ring", "linear", False),
}


def coupling_order(J):
    A = np.abs(J + J.T)
    order = [int(A.sum(1).argmax())]
    left = set(range(len(A))) - set(order)
    while left:
        nxt = max(left, key=lambda j: A[order[-1], j])
        order.append(nxt)
        left.remove(nxt)
    return order


def all_gaps(name, sigmas):
    sp = _space(NV, KV)
    Qs = swap_table(sp)
    Qm = {m: multiswap_table(sp, m) for m in range(2, KV + 1)}
    Afix = {(mx, b): mixer_matrix(NV, KV, b, mx) for mx in ("ring", "complete") for b in BETAS}
    rows = []
    for w in range(64):
        sig = sigmas[w][:N, :N]
        S = longshort_scores(sp, sig)
        T = TAU * S.std()
        h, J = longshort_terms(sig)
        gs = spectral_gap(Qs, S, T)
        base = {"universe": name, "w": w}
        for m, Q in Qm.items():
            rows.append(base | {"method": "multi-swap", "setting": f"m={m}", "ratio": spectral_gap(Q, S, T) / gs})
        rows.append(base | {"method": "locally balanced", "setting": "-",
                            "ratio": chain_gap(informed_matrix(sp, S, T), S, T) / gs})
        order = coupling_order(J)
        for v, (mx, ph, ordered) in VARIANTS.items():
            od = order if ordered else None
            for b, g in itertools.product(BETAS, GS):
                A = mixer_matrix(NV, KV, b, mx, od) if ordered else Afix[(mx, b)]
                Q = proposal_table_fast(NV, KV, h, J, b, g / S.std(), mx, ph, order=od, A=A)
                rows.append(base | {"method": v, "setting": f"beta={b},g={g}", "ratio": spectral_gap(Q, S, T) / gs})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = pd.concat([all_gaps("ETFs", data.load_instances(20)["Sigma"]), all_gaps("stocks", stock_windows())])
    df.to_csv(data.ROOT / "results" / "longshort_fair_tuning_n12.csv", index=False)
    for uni, d in df.groupby("universe", sort=False):
        train, test = d[d.w % 2 == 0], d[d.w % 2 == 1]
        chosen = train.groupby(["method", "setting"]).ratio.median().groupby(level=0).idxmax()
        sel = pd.concat([test[(test.method == m) & (test.setting == s)] for m, s in chosen])
        multi = sel[sel.method == "multi-swap"].set_index("w").ratio
        print(f"\n== {uni}: one setting per method (chosen on 32 train windows), 32 test windows")
        for m, g in sel.groupby("method"):
            r = g.set_index("w").ratio
            beat = (r > multi.loc[r.index]).mean() if m != "multi-swap" else np.nan
            print(f"  {m:30s} {chosen[m][1]:16s} median {r.median():.2f}  "
                  f"beats single swap {(r > 1).mean():4.0%}  beats multi-swap {beat:4.0%}")
