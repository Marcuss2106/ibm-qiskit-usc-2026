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
        "beats_multi_heldout": "81-91%",
        "winner_2q_gates": 540,
        "hw_2q_gates": 86,
        "hw_qpu_seconds": 12,
        "hw_usable": "43%",
        "hw_gap": 0.043, "ideal_gap": 0.090, "swap_gap": 0.061,
        "race_etf_8x8": {"single swap": 1093, "quantum": 1264, "parallel tempering": 1405, "multi-swap": 2175},
    },
}
OUT.write_text(json.dumps(out, indent=1))
print(f"wrote {OUT}  window {out['window_end']}  best book {dict(zip(tickers, out['best_signs']))}")
