"""Count-restricted simulator must match the Qiskit statevector tables exactly."""

import numpy as np
import pytest

from qemcmc.circuits import proposal_circuit, proposal_table, score_terms
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace
from qemcmc.subspace import (
    metropolis_matrix,
    proposal_table_fast,
    spectral_gap,
    swap_table,
)
from tests.test_objective import random_problem


@pytest.mark.parametrize("n,k", [(8, 3), (12, 4)])
@pytest.mark.parametrize("mixer,phase", [("ring", "linear"), ("ring", "full"), ("complete", "ring"), ("ring", "none")])
def test_fast_table_matches_qiskit(n, k, mixer, phase):
    mu, sigma = random_problem(n, 5)
    h, J = score_terms(mu, sigma, 3.0, k)
    order = list(np.random.default_rng(1).permutation(n))
    qc = proposal_circuit(n, h, J, 0.7, 6.0, mixer, phase, order=order)
    slow = proposal_table(StateSpace(n, k), qc)
    fast = proposal_table_fast(n, k, h, J, 0.7, 6.0, mixer, phase, order=order)
    assert np.allclose(fast, slow, atol=1e-10)


def test_swap_table_rows():
    s = StateSpace(8, 3)
    Q = swap_table(s)
    assert np.allclose(Q.sum(1), 1) and np.allclose(Q, Q.T)
    assert ((Q > 0).sum(1) == 15).all()


def test_metropolis_is_stochastic_and_reversible():
    n, k, T = 8, 3, 0.01
    s = StateSpace(n, k)
    mu, sigma = random_problem(n, 6)
    S = enumerate_scores(s, mu, sigma, 3.0)
    P = metropolis_matrix(swap_table(s), S, T)
    assert np.allclose(P.sum(1), 1) and (P >= -1e-15).all()
    pi = np.exp((S - S.max()) / T)
    pi /= pi.sum()
    flow = pi[:, None] * P
    assert np.allclose(flow, flow.T, atol=1e-14)  # detailed balance


def test_spectral_gap_against_dense_eig():
    n, k, T = 8, 3, 0.02
    s = StateSpace(n, k)
    mu, sigma = random_problem(n, 7)
    S = enumerate_scores(s, mu, sigma, 3.0)
    Q = swap_table(s)
    ev = np.sort(np.abs(np.linalg.eigvals(metropolis_matrix(Q, S, T))))[::-1]
    assert spectral_gap(Q, S, T) == pytest.approx(1 - ev[1], abs=1e-9)
