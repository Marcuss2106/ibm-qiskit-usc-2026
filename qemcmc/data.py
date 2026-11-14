"""Data loader: ETF prices -> per-window annualized mean returns and covariance.

See docs/DEVELOPMENT.md §7. Usage:

    python -m qemcmc.data            # build data/instances.npz from cached prices
    python -m qemcmc.data --refresh  # re-download prices first

Ticker order is fixed: the 8-ETF core, then the 12/16/20 additions, so the
n-asset basket is always the first n tickers.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

CORE = ["SPY", "IWM", "EFA", "EEM", "IEF", "TLT", "GLD", "DBC"]
EXT_12 = ["VNQ", "TIP", "LQD", "HYG"]
EXT_16 = ["XLE", "XLK", "XLV", "EWJ"]
EXT_20 = ["XLF", "XLU", "AGG", "SLV"]
TICKERS = CORE + EXT_12 + EXT_16 + EXT_20

START = "2008-12-01"  # first window (ending 2010Q1) needs one year of returns
END = "2026-01-01"  # exclusive in yfinance; covers 2025-12-31
WINDOW = 252  # daily returns per window
ANNUAL = 252  # trading days per year
FIRST_QUARTER = "2010-03-31"
LAST_QUARTER = "2025-12-31"
MAX_FFILL = 2  # fill at most this many consecutive missing days per ticker

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PRICES_CSV = DATA_DIR / "prices.csv"
INSTANCES_NPZ = DATA_DIR / "instances.npz"


def download_prices(tickers=TICKERS, start=START, end=END) -> pd.DataFrame:
    """Adjusted daily closes from Yahoo Finance, columns in `tickers` order."""
    import yfinance as yf

    raw = yf.download(
        tickers, start=start, end=end, auto_adjust=True, progress=False
    )
    prices = raw["Close"][list(tickers)]
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    prices.index.name = "date"
    return prices


def load_prices(refresh: bool = False, path: Path = PRICES_CSV) -> pd.DataFrame:
    """Read cached prices; download (and cache) only if missing or refresh=True."""
    if refresh or not path.exists():
        prices = download_prices()
        path.parent.mkdir(parents=True, exist_ok=True)
        prices.to_csv(path, float_format="%.6f")
    prices = pd.read_csv(path, index_col="date", parse_dates=True)
    return prices[[t for t in TICKERS if t in prices.columns]]


def clean_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill short gaps; raise on bad values in the period windows use."""
    prices = prices.sort_index().ffill(limit=MAX_FFILL)
    if (prices <= 0).any().any():
        raise ValueError("non-positive prices found")
    return prices


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns (portfolio return is linear in weights)."""
    return prices.pct_change().iloc[1:]


def quarter_ends(first: str = FIRST_QUARTER, last: str = LAST_QUARTER):
    return pd.date_range(first, last, freq="QE")


def window_estimates(returns: pd.DataFrame, ends=None, window: int = WINDOW):
    """Annualized mu[W, n] and Sigma[W, n, n] for each window.

    Each window is the last `window` daily returns on or before the quarter end.
    Returns (window_end_dates, mu, Sigma).
    """
    ends = quarter_ends() if ends is None else ends
    n = returns.shape[1]
    dates, mus, sigmas = [], [], []
    for q in ends:
        r = returns.loc[:q].iloc[-window:]
        if len(r) < window:
            raise ValueError(f"window ending {q.date()} has only {len(r)} returns")
        if r.isna().any().any():
            bad = r.columns[r.isna().any()].tolist()
            raise ValueError(f"window ending {q.date()} has missing data for {bad}")
        x = r.to_numpy()
        dates.append(r.index[-1])
        mus.append(ANNUAL * x.mean(axis=0))
        sigmas.append(ANNUAL * np.cov(x, rowvar=False, ddof=1))
    mu = np.asarray(mus).reshape(len(ends), n)
    sigma = np.asarray(sigmas).reshape(len(ends), n, n)
    return pd.DatetimeIndex(dates), mu, sigma


def build_instances(refresh: bool = False, out: Path = INSTANCES_NPZ) -> dict:
    """Prices -> windows -> data/instances.npz. Returns the saved arrays."""
    prices = clean_prices(load_prices(refresh=refresh))
    return save_instances(prices, out)


def save_instances(prices: pd.DataFrame, out: Path = INSTANCES_NPZ) -> dict:
    dates, mu, sigma = window_estimates(daily_returns(prices))
    arrays = {
        # plain unicode arrays, not object arrays, so loading needs no pickle
        "dates": np.array(dates.strftime("%Y-%m-%d"), dtype=str),
        "tickers": np.array(list(prices.columns), dtype=str),
        "mu": mu,
        "Sigma": sigma,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, **arrays)
    return arrays


def load_instances(n: int = len(TICKERS), path: Path = INSTANCES_NPZ) -> dict:
    """Load saved windows, sliced to the first n tickers."""
    z = np.load(path, allow_pickle=False)
    return {
        "dates": pd.DatetimeIndex(z["dates"]),
        "tickers": [str(t) for t in z["tickers"][:n]],
        "mu": z["mu"][:, :n],
        "Sigma": z["Sigma"][:, :n, :n],
    }


def _report(prices: pd.DataFrame, arrays: dict) -> None:
    first = prices.apply(lambda s: s.first_valid_index())
    print("First date per ticker:")
    for t, d in first.items():
        print(f"  {t:4s} {d.date()}")
    print(f"Price rows: {len(prices)}  ({prices.index[0].date()} to {prices.index[-1].date()})")
    sig = arrays["Sigma"]
    eig_min = np.linalg.eigvalsh(sig).min(axis=1)
    print(f"Windows: {len(arrays['dates'])}  ({arrays['dates'][0]} to {arrays['dates'][-1]})")
    print(f"Smallest Sigma eigenvalue across windows: {eig_min.min():.2e}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--refresh", action="store_true", help="re-download prices")
    args = p.parse_args()
    arrays = build_instances(refresh=args.refresh)
    _report(clean_prices(load_prices()), arrays)
    print(f"Saved {INSTANCES_NPZ.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
