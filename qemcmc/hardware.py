"""Hardware run of the long-short proposal circuit (bead 6nz). Setup fixed before running.

Problem: long-short book, 4 long / 4 short on the 8 core ETFs, window ending 2025Q4.
SPY (asset 0) is fixed long, so 7 qubits encode which 3 of the other 7 are long:
35 valid books. Circuit: palindromic ordered-ring XY mixer + ring score phase
(hardware-cheap), beta = 0.75, g = 1 (fair_tuning.py choice for ETFs), gamma =
g / std(S). For every starting book: X gates for its longs, the circuit, measure.

Usage:
    python -m qemcmc.hardware dry   [--backend fake_fez] [--starts ...] [--shots 256]
    python -m qemcmc.hardware pilot  --backend <ibm_name>  --starts 0 17 34
    python -m qemcmc.hardware full   --backend <ibm_name>
    python -m qemcmc.hardware analyze results/hardware/<file>.json

Records (raw counts, job id, backend, transpile stats, QPU seconds) go to
results/hardware/. Analysis compares the measured proposal table with the ideal one.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager

from qemcmc import data
from qemcmc.circuits import proposal_circuit
from qemcmc.longshort import longshort_scores, longshort_terms
from qemcmc.objective import RESULTS_DIR
from qemcmc.subspace import _space, metropolis_matrix, proposal_table_fast, swap_table

N_ASSETS, WINDOW = 8, 63  # 8 core ETFs, window ending 2025Q4
NV, KV = N_ASSETS - 1, N_ASSETS // 2 - 1  # 7 qubits, 3 more longs
BETA, G, TAU = 0.75, 1.0, 0.1
OUT_DIR = RESULTS_DIR / "hardware"


def coupling_order(J: np.ndarray) -> list[int]:
    A = np.abs(J + J.T)
    order = [int(A.sum(1).argmax())]
    left = set(range(len(A))) - set(order)
    while left:
        nxt = max(left, key=lambda j: A[order[-1], j])
        order.append(nxt)
        left.remove(nxt)
    return order


def problem():
    """Everything fixed about the instance: space, scores, circuit terms, settings."""
    sigma = data.load_instances(20)["Sigma"][WINDOW][:N_ASSETS, :N_ASSETS]
    space = _space(NV, KV)
    S = longshort_scores(space, sigma)
    h, J = longshort_terms(sigma)
    order = coupling_order(J)
    gamma = G / S.std()
    return {"space": space, "S": S, "h": h, "J": J, "order": order, "gamma": gamma,
            "T": TAU * S.std(), "tickers": data.TICKERS[:N_ASSETS]}


def ideal_table(p) -> np.ndarray:
    return proposal_table_fast(NV, KV, p["h"], p["J"], BETA, p["gamma"], "ring", "ring", order=p["order"])


def build_circuits(p, starts) -> list[QuantumCircuit]:
    body = proposal_circuit(NV, p["h"], p["J"], BETA, p["gamma"], "ring", "ring", order=p["order"])
    circs = []
    for r in starts:
        qc = QuantumCircuit(NV, name=f"start_{r}")
        for i in p["space"].combos[r]:
            qc.x(int(i))
        qc.compose(body, inplace=True)
        qc.measure_all()
        circs.append(qc)
    return circs


def get_backend(name: str):
    if name.startswith("fake_"):
        from qiskit_ibm_runtime import fake_provider

        cls = "Fake" + "".join(w.capitalize() for w in name.split("_")[1:])
        return getattr(fake_provider, cls)()
    from qiskit_ibm_runtime import QiskitRuntimeService

    return QiskitRuntimeService().backend(name)


def run(backend_name: str, starts, shots: int, tag: str) -> dict:
    p = problem()
    backend = get_backend(backend_name)
    circs = build_circuits(p, starts)
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend, seed_transpiler=7)
    isa = pm.run(circs)
    two_q = [sum(v for k, v in c.count_ops().items() if k in ("cz", "ecr", "cx")) for c in isa]
    depth2q = [c.depth(lambda inst: inst.operation.num_qubits == 2) for c in isa]
    layout = sorted(set(isa[0].layout.final_index_layout())) if isa[0].layout else None

    from qiskit_ibm_runtime import SamplerV2

    sampler = SamplerV2(mode=backend)
    if not backend_name.startswith("fake_"):
        sampler.options.dynamical_decoupling.enable = True
    t0 = time.time()
    job = sampler.run(isa, shots=shots)
    res = job.result()
    wall = time.time() - t0
    counts = [res[i].data.meas.get_counts() for i in range(len(isa))]
    qpu_seconds = None
    try:
        usage = job.metrics().get("usage", {})
        qpu_seconds = usage.get("qpu_charge_time_seconds", usage.get("quantum_seconds"))
    except Exception:
        pass
    rec = {
        "tag": tag, "backend": backend.name, "job_id": getattr(job, "job_id", lambda: None)(),
        "utc": datetime.now(timezone.utc).isoformat(), "shots": shots, "starts": list(map(int, starts)),
        "beta": BETA, "g": G, "gamma": p["gamma"], "order": p["order"], "window": WINDOW,
        "physical_qubits": layout, "two_qubit_gates": two_q, "two_qubit_depth": depth2q,
        "wall_seconds": wall, "qpu_seconds": qpu_seconds, "counts": counts,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{tag}_{backend.name}_{datetime.now():%Y%m%d_%H%M%S}.json"
    path.write_text(json.dumps(rec, indent=1))
    print(f"saved {path.relative_to(data.ROOT)}  job={rec['job_id']}  qpu_seconds={qpu_seconds}  "
          f"wall={wall:.0f}s  2q gates {min(two_q)}-{max(two_q)}  2q depth {min(depth2q)}-{max(depth2q)}")
    return rec


def measured_table(rec, p):
    """Q_hw[start, book] over valid books (rows sum to the usable rate), shape [len(starts), C]."""
    sp = p["space"]
    Q = np.zeros((len(rec["starts"]), sp.size))
    for i, c in enumerate(rec["counts"]):
        for key, v in c.items():
            x = int(key, 2)
            if sp.is_valid_int(x):
                Q[i, int(sp.rank_of_int(x))] += v / rec["shots"]
    return Q


def tvd(a, b) -> float:
    return 0.5 * float(np.abs(a - b).sum())


def analyze(rec) -> dict:
    p = problem()
    sp, S, T = p["space"], p["S"], p["T"]
    Qi = ideal_table(p)
    Qh = measured_table(rec, p)
    starts = rec["starts"]
    usable = Qh.sum(axis=1)
    rows_n = Qh / np.maximum(usable[:, None], 1e-12)
    tv = np.array([tvd(rows_n[i], Qi[r]) for i, r in enumerate(starts)])
    rng = np.random.default_rng(0)  # shot-noise floor: ideal rows sampled with the same usable shots
    floor = np.array([tvd(rng.multinomial(max(int(u * rec["shots"]), 1), Qi[r]) / max(int(u * rec["shots"]), 1), Qi[r])
                      for u, r in zip(usable, starts)])
    out = {"backend": rec["backend"], "starts": len(starts), "shots": rec["shots"],
           "usable_rate_median": float(np.median(usable)), "usable_rate_min": float(usable.min()),
           "tvd_to_ideal_median": float(np.median(tv)), "tvd_shot_noise_floor_median": float(np.median(floor)),
           "qpu_seconds": rec.get("qpu_seconds"),
           "two_qubit_gates_median": float(np.median(rec["two_qubit_gates"]))}
    if len(starts) == sp.size:  # full table: chain-level comparison
        full = np.zeros((sp.size, sp.size))
        full[starts] = Qh  # invalid outcomes -> rejected attempt (stay put)
        out["asymmetry"] = float(np.linalg.norm(full - full.T) / np.linalg.norm(full))
        out["asymmetry_ideal"] = float(np.linalg.norm(Qi - Qi.T) / np.linalg.norm(Qi))
        acc = np.minimum(1.0, np.exp(np.clip((S[None, :] - S[:, None]) / T, -700, 0)))
        P = full * acc
        np.fill_diagonal(P, 0.0)
        np.fill_diagonal(P, 1.0 - P.sum(axis=1))
        ev, vec = np.linalg.eig(P.T)
        k = int(np.argmin(np.abs(ev - 1)))
        stat = np.abs(np.real(vec[:, k]))
        stat /= stat.sum()
        pi = np.exp((S - S.max()) / T)
        pi /= pi.sum()
        mags = np.sort(np.abs(ev))[::-1]

        def gap_of(Pm):
            return float(1 - np.sort(np.abs(np.linalg.eigvals(Pm)))[::-1][1])

        out |= {"gap_hardware": float(1 - mags[1]),
                "gap_ideal": gap_of(metropolis_matrix(Qi, S, T)),
                "gap_single_swap": gap_of(metropolis_matrix(swap_table(sp), S, T)),
                "stationary_tvd_to_target": tvd(stat, pi),
                "p_optimum_target": float(pi.max()), "p_optimum_hardware_chain": float(stat[int(S.argmax())])}
        # Shot-noise baseline: the ideal table sampled with the same shots, no device noise.
        rng = np.random.default_rng(1)
        Qs = np.array([rng.multinomial(rec["shots"], Qi[r]) / rec["shots"] for r in range(sp.size)])
        Ps = Qs * acc
        np.fill_diagonal(Ps, 0.0)
        np.fill_diagonal(Ps, 1.0 - Ps.sum(axis=1))
        evs, vecs = np.linalg.eig(Ps.T)
        ks = int(np.argmin(np.abs(evs - 1)))
        stat_s = np.abs(np.real(vecs[:, ks]))
        stat_s /= stat_s.sum()
        out |= {"asymmetry_shot_noise_floor": float(np.linalg.norm(Qs - Qs.T) / np.linalg.norm(Qs)),
                "gap_shot_noise_only": gap_of(Ps),
                "stationary_tvd_shot_noise_only": tvd(stat_s, pi)}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=["dry", "pilot", "full", "analyze", "info"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--backend", default="fake_fez")
    ap.add_argument("--starts", type=int, nargs="+")
    ap.add_argument("--shots", type=int, default=256)
    a = ap.parse_args()
    if a.mode == "info":
        p = problem()
        print(f"window {data.load_instances(20)['dates'][WINDOW].date()}, books {p['space'].size}, "
              f"ring order {[p['tickers'][i + 1] for i in p['order']]}, gamma {p['gamma']:.3g}")
        return
    if a.mode == "analyze":
        print(json.dumps(analyze(json.loads(open(a.path).read())), indent=1))
        return
    starts = a.starts if a.starts else list(range(_space(NV, KV).size))
    rec = run(a.backend, starts, a.shots, a.mode)
    print(json.dumps(analyze(rec), indent=1))


if __name__ == "__main__":
    main()
