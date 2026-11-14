"""Count-preserving proposal circuits (DEVELOPMENT.md §5.2).

U = M(beta) P(gamma) M(beta)^rev: a block of XY gates, a diagonal score phase, then
the same XY gates in reverse order. Every gate is complex-symmetric (XY with zero
phase, RZ, RZZ), so U equals its transpose and the proposal probabilities
Q[s, s'] = |<s'|U|s>|^2 are symmetric.

Qubit i is ETF i, so Statevector indices and measurement keys equal StateSpace.ints.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import XXPlusYYGate
from qiskit.quantum_info import Statevector

from qemcmc.states import StateSpace

PHASES = ("none", "linear", "ring", "full")
MIXERS = ("ring", "complete")


def score_terms(mu, Sigma, lam: float, k: int):
    """Node weights h[n] and edge weights J[n, n] (upper triangle used) with
    S(x) = sum_i h_i x_i + sum_{i<j} J_ij x_i x_j for 0/1 vectors x."""
    mu, Sigma = np.asarray(mu, float), np.asarray(Sigma, float)
    h = mu / k - lam * np.diag(Sigma) / k**2
    J = -2 * lam * Sigma / k**2
    return h, J


def ring_edges(order) -> list[tuple[int, int]]:
    order = list(order)
    return [(order[t], order[(t + 1) % len(order)]) for t in range(len(order))]


def mixer_edges(n: int, mixer: str = "ring", order=None) -> list[tuple[int, int]]:
    if mixer == "ring":
        return ring_edges(range(n) if order is None else order)
    if mixer == "complete":
        return list(combinations(range(n), 2))
    raise ValueError(f"mixer must be one of {MIXERS}")


def _add_score_phase(qc, h, J, gamma, phase, order):
    """Apply exp(i * gamma * S(x)) up to a global phase, with S restricted by `phase`.

    x_i = (1 - Z_i)/2 gives h_i x_i -> RZ(gamma*h_i) and
    J_ij x_i x_j -> RZ(gamma*J_ij/2) on i and j plus RZZ(-gamma*J_ij/2).
    """
    n = qc.num_qubits
    if phase == "none":
        return
    if phase == "linear":
        pairs = []
    elif phase == "ring":
        pairs = ring_edges(range(n) if order is None else order)
    elif phase == "full":
        pairs = list(combinations(range(n), 2))
    else:
        raise ValueError(f"phase must be one of {PHASES}")
    z = np.array(h, float).copy()
    for i, j in pairs:
        a, b = min(i, j), max(i, j)
        z[a] += J[a, b] / 2
        z[b] += J[a, b] / 2
    for i in range(n):
        if z[i] != 0:
            qc.rz(gamma * z[i], i)
    for i, j in pairs:
        a, b = min(i, j), max(i, j)
        if J[a, b] != 0:
            qc.rzz(-gamma * J[a, b] / 2, a, b)


def proposal_circuit(
    n: int,
    h=None,
    J=None,
    beta: float = 0.5,
    gamma: float = 1.0,
    mixer: str = "ring",
    phase: str = "linear",
    order=None,
    palindromic: bool = True,
) -> QuantumCircuit:
    """M(beta) P(gamma) M(beta)^rev on n qubits (no state prep, no measurement).

    palindromic=False repeats M in the same order instead (for tests only: its
    proposals are generally not symmetric).
    """
    h = np.zeros(n) if h is None else np.asarray(h, float)
    J = np.zeros((n, n)) if J is None else np.asarray(J, float)
    edges = mixer_edges(n, mixer, order)
    qc = QuantumCircuit(n)
    for i, j in edges:
        qc.append(XXPlusYYGate(2 * beta, 0.0), [i, j])
    _add_score_phase(qc, h, J, gamma, phase, order)
    for i, j in reversed(edges) if palindromic else edges:
        qc.append(XXPlusYYGate(2 * beta, 0.0), [i, j])
    return qc


def proposal_table(space: StateSpace, qc: QuantumCircuit) -> np.ndarray:
    """Exact Q[s, s'] over valid portfolios (rank order) by statevector simulation.

    One full 2^n statevector per starting portfolio: fine for n <= 12, slow at 16.
    Ideal circuits keep the holding count, so each row sums to 1.
    """
    if qc.num_qubits != space.n:
        raise ValueError("circuit width must equal n")
    Q = np.empty((space.size, space.size))
    for r, start in enumerate(space.ints):
        probs = Statevector.from_int(int(start), 2**space.n).evolve(qc).probabilities()
        Q[r] = probs[space.ints]
    return Q
