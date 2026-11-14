"""Invariants 1-3 (DEVELOPMENT.md §4) for the palindromic proposal circuit."""

import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from qemcmc.circuits import proposal_circuit, proposal_table, score_terms
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace
from tests.test_objective import random_problem


def make(n, k, mixer, phase, palindromic=True, seed=0, beta=0.6, gamma=4.0):
    mu, sigma = random_problem(n, seed)
    h, J = score_terms(mu, sigma, 3.0, k)
    return proposal_circuit(n, h, J, beta, gamma, mixer, phase, palindromic=palindromic)


@pytest.mark.parametrize("n,k", [(8, 3), (12, 4)])
@pytest.mark.parametrize("mixer", ["ring", "complete"])
@pytest.mark.parametrize("phase", ["none", "linear", "ring", "full"])
def test_palindromic_table_symmetric_and_count_preserving(n, k, mixer, phase):
    if n == 12 and mixer == "complete" and phase != "linear":
        pytest.skip("keep runtime short; complete+linear at n=12 covers it")
    space = StateSpace(n, k)
    Q = proposal_table(space, make(n, k, mixer, phase))
    assert np.allclose(Q, Q.T, atol=1e-10)  # invariant 2
    assert np.allclose(Q.sum(axis=1), 1.0, atol=1e-10)  # invariants 1 and 3
    assert (Q >= -1e-15).all()


def test_non_palindromic_is_not_symmetric():
    """Guards against a vacuous test: M P M (same order twice) breaks symmetry."""
    space = StateSpace(8, 3)
    Q = proposal_table(space, make(8, 3, "ring", "full", palindromic=False))
    assert np.allclose(Q.sum(axis=1), 1.0, atol=1e-10)
    assert not np.allclose(Q, Q.T, atol=1e-6)


def test_score_phase_matches_score():
    """Full phase circuit alone applies exp(i*gamma*S(x)) up to a global phase."""
    n, k, gamma = 8, 3, 0.7
    mu, sigma = random_problem(n, 1)
    h, J = score_terms(mu, sigma, 3.0, k)
    qc = proposal_circuit(n, h, J, beta=0.0, gamma=gamma, phase="full")
    space = StateSpace(n, k)
    S = enumerate_scores(space, mu, sigma, 3.0)
    phases = []
    for r, x in enumerate(space.ints):
        amp = Statevector.from_int(int(x), 2**n).evolve(qc).data[x]
        phases.append(np.angle(amp * np.exp(-1j * gamma * S[r])))
    phases = np.unwrap(np.array(phases))
    assert np.ptp(phases) < 1e-9  # same offset for every valid portfolio


def test_score_terms_reproduce_score():
    n, k, lam = 12, 4, 3.0
    mu, sigma = random_problem(n, 2)
    h, J = score_terms(mu, sigma, lam, k)
    space = StateSpace(n, k)
    iu = np.triu_indices(n, 1)
    x = space.bits.astype(float)
    pair = (x[:, iu[0]] * x[:, iu[1]]) @ J[iu]
    assert np.allclose(x @ h + pair, enumerate_scores(space, mu, sigma, lam))


def test_zero_mixing_is_identity():
    space = StateSpace(8, 3)
    Q = proposal_table(space, make(8, 3, "ring", "linear", beta=0.0))
    assert np.allclose(Q, np.eye(space.size))
