"""Data loader tests on synthetic prices (no network)."""

import numpy as np
import pandas as pd
import pytest

from qemcmc import data


@pytest.fixture
def prices():
    rng = np.random.default_rng(0)
    days = pd.bdate_range("2008-12-01", "2025-12-31")
    n = 5
    rets = rng.normal(0.0003, 0.01, size=(len(days), n))
    p = 100 * np.cumprod(1 + rets, axis=0)
    return pd.DataFrame(p, index=days, columns=[f"A{i}" for i in range(n)])


def test_windows_shape_and_symmetry(prices):
    dates, mu, sigma = data.window_estimates(data.daily_returns(prices))
    assert len(dates) == 64
    assert mu.shape == (64, 5) and sigma.shape == (64, 5, 5)
    assert np.isfinite(mu).all() and np.isfinite(sigma).all()
    assert np.allclose(sigma, sigma.transpose(0, 2, 1))
    assert (np.linalg.eigvalsh(sigma) > 0).all()
    assert (dates <= data.quarter_ends()).all()


def test_window_matches_direct_computation(prices):
    r = data.daily_returns(prices)
    dates, mu, sigma = data.window_estimates(r)
    w = r.loc[:"2017-06-30"].iloc[-252:]
    i = list(data.quarter_ends()).index(pd.Timestamp("2017-06-30"))
    assert np.allclose(mu[i], 252 * w.mean().to_numpy())
    assert np.allclose(sigma[i], 252 * w.cov().to_numpy())


def test_short_gap_filled_long_gap_raises(prices):
    p = prices.copy()
    p.iloc[1000:1002, 0] = np.nan  # 2 days: filled
    data.window_estimates(data.daily_returns(data.clean_prices(p)))
    p.iloc[2000:2010, 1] = np.nan  # 10 days: left as NaN
    with pytest.raises(ValueError, match="missing data"):
        data.window_estimates(data.daily_returns(data.clean_prices(p)))


def test_save_load_roundtrip_and_prefix_slice(prices, tmp_path):
    out = tmp_path / "inst.npz"
    saved = data.save_instances(prices, out)
    z = data.load_instances(n=3, path=out)
    assert z["tickers"] == ["A0", "A1", "A2"]
    assert len(z["dates"]) == 64
    assert np.array_equal(z["mu"], saved["mu"][:, :3])
    assert np.array_equal(z["Sigma"], saved["Sigma"][:, :3, :3])


def test_ticker_order_nests_baskets():
    assert data.TICKERS[:8] == data.CORE
    assert len(data.TICKERS) == len(set(data.TICKERS)) == 20
