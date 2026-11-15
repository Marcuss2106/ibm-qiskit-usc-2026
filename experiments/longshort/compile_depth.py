"""Compiled cost of the proposal-circuit variants on IBM Heron device models (offline).

Transpiles the palindromic circuit (mixer, phase, reversed mixer) for the long-short
book at 11 qubits (6 long / 6 short) and 15 qubits (8 long / 8 short) onto FakeFez and
FakeTorino, optimization level 3, best of 3 seeds. Reports two-qubit gate count and
two-qubit depth. Run from the repo root:
    PYTHONPATH=. python experiments/longshort/compile_depth.py
"""
import numpy as np
from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeTorino

from qemcmc import data
from qemcmc.circuits import proposal_circuit
from qemcmc.longshort import longshort_terms

VARIANTS = [  # (label, mixer, phase, ordered)
    ("ring mixer + linear phase (hardware target)", "ring", "linear", False),
    ("ring mixer + ring phase", "ring", "ring", False),
    ("ordered ring + ordered ring phase", "ring", "ring", True),
    ("ring mixer + full phase", "ring", "full", False),
    ("complete mixer + full phase (best in simulation)", "complete", "full", False),
]


def coupling_order(J):
    A = np.abs(J + J.T)
    order = [int(A.sum(1).argmax())]
    left = set(range(len(A))) - set(order)
    while left:
        nxt = max(left, key=lambda j: A[order[-1], j])
        order.append(nxt)
        left.remove(nxt)
    return order


def two_qubit_stats(qc):
    ops = qc.count_ops()
    n2q = sum(v for k, v in ops.items() if k in ("cz", "ecr", "cx"))
    depth2q = qc.depth(lambda inst: inst.operation.num_qubits == 2)
    return n2q, depth2q


if __name__ == "__main__":
    sig = data.load_instances(20)["Sigma"][0]
    for backend in (FakeFez(), FakeTorino()):
        print(f"\n== {backend.name} ({backend.num_qubits} qubits)")
        for n in (12, 16):
            h, J = longshort_terms(sig[:n, :n])
            nv = n - 1
            print(f"  {nv} qubits ({n // 2} long / {n // 2} short):")
            for label, mixer, phase, ordered in VARIANTS:
                order = coupling_order(J) if ordered else None
                qc = proposal_circuit(nv, h, J, beta=0.3, gamma=1.0, mixer=mixer, phase=phase, order=order)
                best = min((two_qubit_stats(transpile(qc, backend, optimization_level=3, seed_transpiler=s))
                            for s in range(3)), key=lambda t: t[0])
                print(f"    {label:50s} 2q gates {best[0]:5d}   2q depth {best[1]:4d}")
