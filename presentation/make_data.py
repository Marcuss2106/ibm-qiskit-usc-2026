"""Export the real numbers the slides use to presentation/data.json.

Run with the project environment (needs qemcmc), from the repo root:
    PYTHONPATH=. qiskit-env/bin/python presentation/make_data.py
The manim scenes only read the JSON, so the manim environment needs no project deps.
"""
import json
from pathlib import Path

import numpy as np

from qemcmc import data, hardware as hw
from qemcmc.longshort import book_signs

OUT = Path(__file__).with_name("data.json")

inst = data.load_instances(8)
sigma = inst["Sigma"][hw.WINDOW]
d = np.sqrt(np.diag(sigma))
corr = sigma / np.outer(d, d)
tickers = inst["tickers"]

p = hw.problem()
space, S = p["space"], p["S"]
signs = book_signs(space)  # [35, 8], SPY first and fixed long
best = int(S.argmax())
worst = int(S.argmin())
risk = -S  # book variance
lo, hi = float(risk.min()), float(risk.max())

out = {
    "window_end": str(inst["dates"][hw.WINDOW].date()),
    "tickers": tickers,
    "corr": np.round(corr, 3).tolist(),
    "best_signs": signs[best].astype(int).tolist(),  # +1 long, -1 short, ticker order
    "worst_signs": signs[worst].astype(int).tolist(),
    "risk_best_norm": 0.0,
    "risk_worst_norm": 1.0,
    "risk_median_norm": float((np.median(risk) - lo) / (hi - lo)),
    "numbers": {
        "mv_one_optimum_windows": "64 of 64",
        "mv_quantum_vs_swap": "0.5-0.8x",
        "random_corr_median_optima": 12,
        "ls_median_optima_8x8_etf": 13,
        "ls_greedy_fail_8x8_etf": "~80%",
        "bars_etf_fair": {"single swap": 1.0, "multi-swap (tuned)": 2.22, "quantum (all-pairs mixer)": 2.67},
        "quantum_phase_off_etf": 1.84,
        "beats_multi_heldout": "81–91%",
        "locally_balanced_etf": 3.42,  # research_results.md §5.2 (fair tuning, ETFs)
        "locally_balanced_checks": 30,  # k(n-k) = 5 x 6 score checks per step at 6 vs 6 with SPY fixed
        "winner_2q_gates": 540,
        "hw_2q_gates": 86,
        "hw_qpu_seconds": 12,
        "hw_usable": "43%",
        "hw_gap": 0.043, "ideal_gap": 0.090, "swap_gap": 0.061,
        "race_etf_8x8": {"single swap": 1093, "quantum": 1264, "parallel tempering": 1405, "multi-swap": 2175},
    },
}
# ------------------------------------------------------------- 3D landscape peaks
# One window (ending 2022Q2) where the 8 vs 8 long-short book has the median 13 local
# optima. Each real local optimum becomes one peak: height = its score (relative to the
# median book), width = share of starts whose steepest ascent ends there, position =
# classical MDS of swap distances between the optima.
import pandas as pd

from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.longshort import longshort_scores
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

W3D = 49
inst16 = data.load_instances(16)
mu16, sig16 = inst16["mu"][W3D], inst16["Sigma"][W3D]


def peaks(space, S, signs):
    nb = space.swap_neighbors()
    opt = np.nonzero(local_optima(S, nb))[0]
    ends = greedy_endpoints(S, nb)
    share = np.array([(ends == o).mean() for o in opt])
    X = signs[opt].astype(float)
    D2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    if len(opt) > 1:  # classical MDS
        J = np.eye(len(opt)) - 1 / len(opt)
        B = -0.5 * J @ D2 @ J
        w, v = np.linalg.eigh(B)
        P = v[:, -2:] * np.sqrt(np.maximum(w[-2:], 0))
        P = P - P.mean(0)
        P = P / (np.abs(P).max() + 1e-12) * 0.8
    else:
        P = np.zeros((1, 2))
    med = np.median(S)
    h = (S[opt] - med) / (S.max() - med)
    return [{"x": float(p[0]), "y": float(p[1]), "h": float(hh), "share": float(sh),
             "best": bool(o == S.argmax())} for p, hh, sh, o in zip(P, h, share, opt)]


lo_space = StateSpace(16, 5)
lo_S = enumerate_scores(lo_space, mu16, sig16, 3.0)
ls_space = StateSpace(15, 7)
ls_S = longshort_scores(ls_space, sig16)
out["landscape3d"] = {
    "window_end": str(inst16["dates"][W3D].date()),
    "long_only": peaks(lo_space, lo_S, lo_space.bits),
    "long_short": peaks(ls_space, ls_S, book_signs(ls_space)),
}

# ------------------------------------------------------------- proposal heatmaps
# Hardware-sized instance (4 vs 4, 35 books, window 2025Q4): where each move can go
# from each book. Books ordered by score (worst first).
from qemcmc.subspace import proposal_table_fast, swap_table

order = np.argsort(S)
gamma = 3.0 / S.std()  # complete mixer + full phase, beta 0.3, g 3 (fair_tuning choice)
Qq = proposal_table_fast(hw.NV, hw.KV, p["h"], p["J"], 0.3, gamma, "complete", "full")
Qs = swap_table(space)
out["proposals"] = {
    "one_swap": np.round(Qs[np.ix_(order, order)], 4).tolist(),
    "quantum": np.round(Qq[np.ix_(order, order)], 4).tolist(),
}

# ------------------------------------------------------------- per-quarter results
# Held-out (odd) quarters at 6 vs 6: quantum (complete + full, setting chosen on train)
# divided by tuned multi-swap (setting chosen on train). Above 1 = quantum explores faster.
ft = pd.read_csv(data.ROOT / "results" / "longshort_fair_tuning_n12.csv")
dates = data.load_instances(20)["dates"]
pq = {}
for uni, d in ft.groupby("universe"):
    tr = d[d.w % 2 == 0]
    best = tr.groupby(["method", "setting"]).ratio.median().groupby(level=0).idxmax()
    te = d[d.w % 2 == 1]
    q = te[(te.method == "complete+full") & (te.setting == best["complete+full"][1])].set_index("w").ratio
    m = te[(te.method == "multi-swap") & (te.setting == best["multi-swap"][1])].set_index("w").ratio
    pq[uni] = {"quarters": [str(dates[w].date()) for w in q.index],
               "ratio": [round(float(q[w] / m[w]), 3) for w in q.index]}
out["per_quarter"] = pq

OUT.write_text(json.dumps(out, indent=1))
for name in ("long_only", "long_short"):
    pk = out["landscape3d"][name]
    print(f"{name}: {len(pk)} peaks, best share {max(x['share'] for x in pk if x['best']):.2f}")
for uni, v in pq.items():
    r = np.array(v["ratio"])
    print(f"{uni}: {len(r)} held-out quarters, quantum beats tuned multi-swap in {(r > 1).mean():.0%}")
print(f"wrote {OUT}  window {out['window_end']}  best book {dict(zip(tickers, out['best_signs']))}")
