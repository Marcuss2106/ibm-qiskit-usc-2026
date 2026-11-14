"""Score, state numbering and answer key tests (synthetic data, no network)."""

from itertools import combinations
from math import comb

import numpy as np
import pandas as pd
import pytest

from qemcmc.objective import answer_key, enumerate_scores, score, summarize
from qemcmc.states import StateSpace


def random_problem(n, seed=0):
    rng = np.random.default_rng(seed)
    mu = rng.normal(0.08, 0.1, n)
    a = rng.normal(size=(n, n)) * 0.1
    return mu, a @ a.T + 0.01 * np.eye(n)


@pytest.mark.parametrize("n,k", [(8, 3), (12, 4), (16, 5)])
def test_state_space_counts_and_order(n, k):
    s = StateSpace(n, k)
    assert s.size == comb(n, k)
    assert (s.bits.sum(axis=1) == k).all()
    assert [tuple(c) for c in s.combos] == list(combinations(range(n), k))
    assert len(set(s.ints.tolist())) == s.size


def test_rank_roundtrips():
    s = StateSpace(12, 4)
    ranks = np.arange(s.size)
    assert (s.rank_of_int(s.ints) == ranks).all()
    for r in [0, 1, 200, s.size - 1]:
        assert s.rank_of_combo(s.combos[r]) == r
        assert s.rank_of_bits(s.bits[r]) == r
        assert int(s.bitstring(r), 2) == s.ints[r]  # Qiskit key -> int
        assert s.bitstring(r)[::-1].index("1") == s.combos[r][0]  # ETF 0 rightmost


def test_invalid_ints_rejected():
    s = StateSpace(8, 3)
    assert not s.is_valid_int(0b11).any()  # 2 ones
    assert not s.is_valid_int(0b1111).any()  # 4 ones
    assert not s.is_valid_int(1 << 9 | 0b11).any()  # outside n bits
    with pytest.raises(ValueError):
        s.rank_of_int([0b111, 0b11])


def test_vectorized_score_matches_naive_loop():
    n, k, lam = 12, 4, 3.0
    mu, sigma = random_problem(n)
    s = StateSpace(n, k)
    fast = enumerate_scores(s, mu, sigma, lam)
    for r in range(0, s.size, 7):
        c = s.combos[r]
        naive = sum(mu[i] for i in c) / k - lam / k**2 * sum(
            sigma[i, j] for i in c for j in c
        )
        assert fast[r] == pytest.approx(naive, rel=1e-12, abs=1e-14)
    assert np.allclose(fast, score(s.bits, mu, sigma, lam, k))


def test_optimum_beats_random_portfolios():
    n, k, lam = 16, 5, 1.0
    mu, sigma = random_problem(n, seed=1)
    s = StateSpace(n, k)
    s_star = summarize(enumerate_scores(s, mu, sigma, lam))["s_star"]
    rng = np.random.default_rng(2)
    for _ in range(1000):
        x = np.zeros(n)
        x[rng.choice(n, k, replace=False)] = 1
        assert score(x, mu, sigma, lam, k) <= s_star + 1e-12


def test_summarize_ties_and_gap():
    out = summarize(np.array([1.0, 3.0, 3.0, 2.5]))
    assert out["s_star"] == 3.0 and out["best_rank"] == 1
    assert out["n_ties"] == 2
    assert out["second_gap"] == pytest.approx(0.5)


def test_answer_key_rows():
    n, k = 8, 3
    mu, sigma = random_problem(n)
    inst = {
        "dates": pd.DatetimeIndex(["2020-03-31", "2020-06-30"]),
        "tickers": [f"T{i}" for i in range(n)],
        "mu": np.stack([mu, -mu]),
        "Sigma": np.stack([sigma, sigma]),
    }
    df = answer_key(n, k, lams=[1.0, 10.0], instances=inst)
    assert len(df) == 4
    s = StateSpace(n, k)
    for _, row in df.iterrows():
        w = 0 if row.window_end == "2020-03-31" else 1
        scores = enumerate_scores(s, inst["mu"][w], sigma, row.lam)
        assert row.s_star == pytest.approx(scores.max())
        assert row.best_tickers.count("+") == k - 1
