"""Long-short book: score and circuit terms (no network)."""

import numpy as np

from qemcmc.longshort import book_signs, longshort_scores, longshort_terms
from qemcmc.states import StateSpace
from qemcmc.subspace import phase_scores
from tests.test_objective import random_problem


def test_scores_match_direct_risk_and_balance():
    n = 8
    _, sigma = random_problem(n, 3)
    space = StateSpace(n - 1, n // 2 - 1)
    s = book_signs(space)
    assert (s.sum(axis=1) == 0).all()  # half long, half short
    assert (s[:, 0] == 1).all()  # asset 0 fixed long
    S = longshort_scores(space, sigma)
    for r in [0, 5, space.size - 1]:
        w = s[r] / n
        assert np.isclose(S[r], -w @ sigma @ w)


def test_terms_reproduce_score_up_to_constant():
    n = 10
    _, sigma = random_problem(n, 4)
    space = StateSpace(n - 1, n // 2 - 1)
    h, J = longshort_terms(sigma)
    diff = phase_scores(space, h, J, "full") - longshort_scores(space, sigma)
    assert np.ptp(diff) < 1e-12
