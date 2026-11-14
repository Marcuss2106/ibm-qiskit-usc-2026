"""Stock-universe landscape test (5 of 16), same settings grid as etf_fixes.py.

Rule (fixed before looking at results): the 2 largest US stocks by market cap at
the start of 2010 in each of 8 sectors, still trading under the same ticker
(survivorship bias acknowledged). Sector picks are approximate, from memory.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, group_of, local_optima
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

STOCKS = [
    "AAPL", "MSFT",  # tech
    "XOM", "CVX",  # energy
    "JPM", "WFC",  # financials
    "JNJ", "PFE",  # health care
    "WMT", "PG",  # staples
    "GE", "UPS",  # industrials (UTX excluded: became RTX)
    "T", "VZ",  # telecom
    "MCD", "AMZN",  # discretionary
]
cache = Path(sys.argv[1])
if not cache.exists():
    data.download_prices(STOCKS).to_csv(cache, float_format="%.6f")
prices = pd.read_csv(cache, index_col="date", parse_dates=True)[STOCKS]
print("first dates:", prices.apply(lambda s: s.first_valid_index().date()).unique())
returns = data.daily_returns(data.clean_prices(prices))

n, k = 16, 5
sp = StateSpace(n, k)
nb = sp.swap_neighbors()
rows = []
for window in [252, 63]:
    _, mu, S = data.window_estimates(returns, window=window)
    for lam, a in [(3, 0.0), (10, 0.0), (3, 0.9), (3, 1.0)]:
        opts, succ = [], []
        for m, s in zip(mu, S):
            m = m.mean() + (1 - a) * (m - m.mean())
            sc = enumerate_scores(sp, m, s, lam)
            opts.append(int(local_optima(sc, nb).sum()))
            succ.append(float((greedy_endpoints(sc, nb) == sc.argmax()).mean()))
        o = np.array(opts)
        g = pd.Series([group_of(c) for c in o]).value_counts()
        rows.append(
            {
                "window": window, "lam": lam, "shrink": a,
                "n=1": g.get("1", 0), "2-5": g.get("2-5", 0), ">5": g.get(">5", 0),
                "median_opt": np.median(o), "max_opt": o.max(),
                "median_greedy": round(float(np.median(succ)), 2),
                "min_greedy": round(float(np.min(succ)), 2),
            }
        )
print("5 of 16 stocks, 64 quarterly windows (counts = windows per group)")
print(pd.DataFrame(rows).to_string(index=False))
