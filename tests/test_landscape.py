"""Landscape check tests: neighbor table, local optima, greedy basins."""

import numpy as np
import pandas as pd
import pytest

from qemcmc.landscape import analyze, greedy_endpoints, group_of, local_optima, select_windows
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace
from tests.test_objective import random_problem


@pytest.mark.parametrize("n,k", [(8, 3), (12, 4)])
def test_swap_neighbors(n, k):
    s = StateSpace(n, k)
    nb = s.swap_neighbors()
    assert nb.shape == (s.size, k * (n - k))
    for r in [0, 17, s.size - 1]:
        assert len(set(nb[r].tolist())) == k * (n - k)  # all distinct
        diff = (s.bits[nb[r]] != s.bits[r]).sum(axis=1)
        assert (diff == 2).all()  # exactly one ETF out, one in
    # symmetric: if b is a neighbor of a, a is a neighbor of b
    a, b = 5, nb[5, 3]
    assert a in nb[b]


def test_local_optima_match_naive():
    n, k = 12, 4
    s = StateSpace(n, k)
    nb = s.swap_neighbors()
    mu, sigma = random_problem(n, seed=3)
    scores = enumerate_scores(s, mu, sigma, 30.0)
    fast = local_optima(scores, nb)
    naive = np.array([all(scores[j] <= scores[i] for j in nb[i]) for i in range(s.size)])
    assert (fast == naive).all()
    assert fast[np.argmax(scores)]  # global optimum is a local optimum


def test_greedy_ends_at_local_optima():
    n, k = 12, 4
    s = StateSpace(n, k)
    nb = s.swap_neighbors()
    mu, sigma = random_problem(n, seed=4)
    scores = enumerate_scores(s, mu, sigma, 30.0)
    ends = greedy_endpoints(scores, nb)
    assert local_optima(scores, nb)[ends].all()
    assert (scores[ends] >= scores - 1e-12).all()
    # naive steepest ascent from a few starts
    for start in [0, 100, 400]:
        cur = start
        while scores[nb[cur]].max() > scores[cur] + 1e-10:
            cur = nb[cur][np.argmax(scores[nb[cur]])]
        assert ends[start] == cur


def test_single_peak_is_easy():
    s = StateSpace(8, 3)
    scores = s.bits @ np.arange(8.0)  # additive: one optimum, greedy always wins
    out = analyze(scores, s.swap_neighbors())
    assert out == {"n_local_opt": 1, "group": "1", "greedy_success": 1.0}


def test_groups_and_selection():
    assert [group_of(c) for c in (1, 2, 5, 6)] == ["1", "2-5", "2-5", ">5"]
    df = pd.DataFrame(
        {
            "window_end": [f"2020-{m:02d}-01" for m in range(1, 13)],
            "lam": 1.0,
            "group": ["1"] * 8 + ["2-5"] * 3 + [">5"],
        }
    )
    pick = select_windows(df, 1.0, per_group=2)
    assert pick["group"].value_counts().to_dict() == {"1": 2, "2-5": 2, ">5": 1}
    assert pick.equals(select_windows(df, 1.0, per_group=2))  # deterministic
