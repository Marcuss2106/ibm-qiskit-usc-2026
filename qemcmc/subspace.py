"""Count-restricted simulation of the proposal circuit and exact chain diagnostics.

The circuit in qemcmc/circuits.py keeps the holding count, so it acts on the
C(n, k) valid portfolios only. Writing the mixer block's operator as A (gates
g1..gm applied in order), the palindromic circuit is U = A^T P A, because every
XY gate is complex-symmetric. A depends only on (n, k, beta, mixer, order), so it is
built once and reused for every window; each table then costs one C x C product.

Matches qemcmc.circuits.proposal_table (tested at 3/8 and 4/12) but is ~100x faster
at 5 of 16.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from qemcmc.circuits import mixer_edges, ring_edges
from qemcmc.states import StateSpace


@lru_cache(maxsize=8)
def _space(n: int, k: int) -> StateSpace:
    return StateSpace(n, k)


def _edge_pairs(space: StateSpace, a: int, b: int):
    """Ranks (r, r2) where r holds a but not b and r2 is r with a and b swapped."""
    has_a = space.bits[:, a] == 1
    has_b = space.bits[:, b] == 1
    r = np.nonzero(has_a & ~has_b)[0]
    flipped = space.ints[r] ^ ((1 << a) | (1 << b))
    return r, space.rank_of_int(flipped)


def mixer_matrix(n: int, k: int, beta: float, mixer: str = "ring", order=None) -> np.ndarray:
    """A = g_m ... g_1 restricted to valid portfolios (C x C, complex).

    Each XY gate XXPlusYYGate(2*beta, 0) rotates the |01>, |10> pair:
    [[cos b, -i sin b], [-i sin b, cos b]].
    """
    space = _space(n, k)
    A = np.eye(space.size, dtype=complex)
    c, s = np.cos(beta), -1j * np.sin(beta)
    for a, b in mixer_edges(n, mixer, order):
        r, r2 = _edge_pairs(space, a, b)
        top, bot = A[r].copy(), A[r2]
        A[r] = c * top + s * bot
        A[r2] = s * top + c * bot
    return A


def phase_scores(space: StateSpace, h, J, phase: str = "linear", order=None) -> np.ndarray:
    """The part of S(x) the circuit's score phase encodes, per valid portfolio."""
    x = space.bits.astype(float)
    if phase == "none":
        return np.zeros(space.size)
    out = x @ np.asarray(h, float)
    if phase == "linear":
        return out
    if phase == "ring":
        pairs = ring_edges(range(space.n) if order is None else order)
    elif phase == "full":
        pairs = [(i, j) for i in range(space.n) for j in range(i + 1, space.n)]
    else:
        raise ValueError(f"unknown phase {phase!r}")
    for i, j in pairs:
        a, b = min(i, j), max(i, j)
        out = out + J[a, b] * x[:, a] * x[:, b]
    return out


def proposal_table_fast(
    n: int, k: int, h, J, beta: float, gamma: float,
    mixer: str = "ring", phase: str = "linear", order=None, A=None,
) -> np.ndarray:
    """Q[s, s'] = |<s'|A^T P A|s>|^2 over valid portfolios, rank order."""
    space = _space(n, k)
    if A is None:
        A = mixer_matrix(n, k, beta, mixer, order)
    p = np.exp(1j * gamma * phase_scores(space, h, J, phase, order))
    U = A.T @ (p[:, None] * A)  # U[s', s] = <s'|U|s>
    return (np.abs(U) ** 2).T


def swap_table(space: StateSpace) -> np.ndarray:
    """Uniform single-swap proposal (local Kawasaki) as a dense C x C table."""
    nb = space.swap_neighbors()
    Q = np.zeros((space.size, space.size))
    np.put_along_axis(Q, nb, 1.0 / nb.shape[1], axis=1)
    return Q


def metropolis_matrix(Q: np.ndarray, scores: np.ndarray, T: float) -> np.ndarray:
    """Transition matrix for maximizing `scores` at temperature T with symmetric Q."""
    accept = np.minimum(1.0, np.exp(np.clip((scores[None, :] - scores[:, None]) / T, -700, 0)))
    P = Q * accept
    np.fill_diagonal(P, 0.0)
    np.fill_diagonal(P, 1.0 - P.sum(axis=1))
    return P


def spectral_gap(Q: np.ndarray, scores: np.ndarray, T: float) -> float:
    """1 - |second-largest eigenvalue| of the Metropolis chain (exact).

    The chain is reversible w.r.t. pi ~ exp(S/T), so D^1/2 P D^-1/2 is symmetric.
    """
    P = metropolis_matrix(Q, scores, T)
    logpi = (scores - scores.max()) / T
    d = np.exp(logpi / 2)
    Ssym = (d[:, None] * P) / d[None, :]
    Ssym = (Ssym + Ssym.T) / 2
    ev = np.sort(np.abs(np.linalg.eigvalsh(Ssym)))[::-1]
    return float(1.0 - ev[1])
