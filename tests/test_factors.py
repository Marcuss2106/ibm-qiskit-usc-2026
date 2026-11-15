"""Factor-selection pilot: exact R^2, posterior, pairwise approximation (no network)."""

import numpy as np

from qemcmc.factors import log_posterior, pairwise_r2, posterior_stats, r2_all
from qemcmc.states import StateSpace


def synthetic(n=8, N=300, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(N, n)) @ rng.normal(size=(n, n)) * 0.3 + rng.normal(size=(N, n))
    y = X[:, :3] @ np.array([1.0, -0.5, 0.3]) + rng.normal(size=N)
    C = np.corrcoef(np.column_stack([y, X]), rowvar=False)
    return X, y, C[0, 1:], C[1:, 1:]


def test_r2_matches_least_squares():
    X, y, c, R = synthetic()
    s = StateSpace(8, 3)
    r2 = r2_all(s, c, R)
    for r in [0, 10, 40, s.size - 1]:
        Z = np.column_stack([np.ones(len(y)), X[:, s.combos[r]]])
        resid = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
        assert np.isclose(r2[r], 1 - resid.var() / y.var())


def test_pairwise_exact_for_orthogonal_factors():
    c = np.array([0.5, 0.3, -0.2, 0.1, 0.4])
    s = StateSpace(5, 2)
    assert np.allclose(pairwise_r2(s, c, np.eye(5)), r2_all(s, c, np.eye(5)))


def test_log_posterior_monotone_in_r2():
    r2 = np.linspace(0.0, 0.9, 10)
    assert (np.diff(log_posterior(r2)) > 0).all()


def test_posterior_stats_single_peak():
    s = StateSpace(8, 3)
    S = s.bits @ np.arange(8.0)  # additive: one mode
    out = posterior_stats(S, s.swap_neighbors())
    assert out["n_local_opt"] == 1 and out["mass_other_modes"] < 1e-12
