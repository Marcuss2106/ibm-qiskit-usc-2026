"""Export the extra real data the LinkedIn loop needs to presentation/linkedin_data.json.

Run with the project environment (needs qemcmc and qiskit-ibm-runtime), from the repo root:
    PYTHONPATH=. qiskit-env/bin/python presentation/linkedin_data.py
The manim scene (linkedin_gif.py) only reads JSON, like slides.py.
"""
import csv
import json
from pathlib import Path

import numpy as np

from qemcmc import data, hardware as hw

OUT = Path(__file__).with_name("linkedin_data.json")
N_ETF = 16

# ---- prices: month-end closes of the 16-ETF basket, normalised to 1 at the start
with open(data.ROOT / "data" / "prices.csv") as f:
    rows = list(csv.reader(f))
head, body = rows[0], rows[1:]
tick = data.TICKERS[:N_ETF]
cols = [head.index(t) for t in tick]
month_end = [i for i in range(len(body)) if i == len(body) - 1 or body[i][0][:7] != body[i + 1][0][:7]]
px = np.array([[float(body[i][c]) for c in cols] for i in month_end])
logp = np.log(px / px[0])

# ---- correlation of the 16 ETFs, last quarter (same window as the hardware run)
inst = data.load_instances(N_ETF)
sig = inst["Sigma"][hw.WINDOW]
d = np.sqrt(np.diag(sig))
corr16 = sig / np.outer(d, d)

# ---- hardware: chip layout, the qubits we used, the measured proposal table
rec = json.loads(sorted((data.ROOT / "results" / "hardware").glob("full_ibm_marrakesh_*.json"))[-1].read_text())
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh  # noqa: E402

edges = sorted({tuple(sorted(e)) for e in FakeMarrakesh().coupling_map.get_edges()})
n_q = 1 + max(max(e) for e in edges)
# Heron heavy-hex: rows of 16 qubits (r*20 .. r*20+15), then 4 bridge qubits (r*20+16 .. r*20+19)
pos = {}
for q in range(n_q):
    r, k = divmod(q, 20)
    if k < 16:
        pos[q] = (k, -2 * r)
for q in range(n_q):
    r, k = divmod(q, 20)
    if k >= 16:
        nb = [b if a == q else a for a, b in edges if q in (a, b)]
        pos[q] = (float(np.mean([pos[x][0] for x in nb if x in pos and divmod(x, 20)[1] < 16])), -2 * r - 1)
bad = [e for e in edges if np.hypot(pos[e[0]][0] - pos[e[1]][0], pos[e[0]][1] - pos[e[1]][1]) > 1.01]
assert not bad, f"layout guess wrong for {len(bad)} edges"

p = hw.problem()
order = np.argsort(p["S"])  # books worst first, as in data.json
Q_hw = hw.measured_table(rec, p)  # rows: starts (= book ranks 0..34), cols: books
Q_hw = Q_hw[np.ix_(order, order)]
valid_frac = float(Q_hw.sum(1).mean())

sp = p["space"]
start0 = rec["counts"][0]
sample = sorted(start0.items(), key=lambda kv: -kv[1])[:24]
stream = [{"bits": k, "valid": bool(sp.is_valid_int(int(k, 2)))} for k, _ in sample]

out = {
    "tickers16": tick,
    "price_dates": [body[month_end[0]][0][:7], body[month_end[-1]][0][:7]],
    "logp": np.round(logp, 3).T.tolist(),  # [ticker][month]
    "n_quarters": int(len(inst["dates"])),
    "corr16": np.round(corr16, 3).tolist(),
    "chip": {"backend": rec["backend"], "positions": [pos[q] for q in range(n_q)], "edges": edges,
             "used": rec["physical_qubits"]},
    "hw_table": np.round(Q_hw, 4).tolist(),
    # which ETFs (qubit index) each book holds long, books in the same order as data.json proposals
    "book_longs": [[int(i) for i in np.asarray(sp.combos)[r]] for r in order],
    "hw_usable": round(valid_frac, 3),
    "hw_shots": rec["shots"], "hw_starts": len(rec["starts"]), "hw_qpu_seconds": rec["qpu_seconds"],
    "stream": stream,
}
OUT.write_text(json.dumps(out))
print(f"wrote {OUT}  ({n_q} qubits, usable {valid_frac:.0%}, {len(month_end)} months)")
