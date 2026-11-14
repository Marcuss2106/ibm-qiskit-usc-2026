"""Do mu shrinkage and/or shorter windows make the 5-of-16 ETF landscape rugged?

mu_shrunk = mean(mu) + (1 - a) * (mu - mean(mu)). With equal weights the common
mean adds the same constant to every portfolio, so a = 1 is risk-only.
"""
import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, group_of, local_optima
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

n, k, lam = 16, 5, 3.0
sp = StateSpace(n, k)
nb = sp.swap_neighbors()
returns = data.daily_returns(data.clean_prices(data.load_prices()))[data.TICKERS[:n]]

rows = []
for window in [252, 126, 63]:
    _, mu, S = data.window_estimates(returns, window=window)
    for a in [0.0, 0.5, 0.8, 0.9, 1.0]:
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
                "window": window,
                "shrink": a,
                "n=1": g.get("1", 0),
                "2-5": g.get("2-5", 0),
                ">5": g.get(">5", 0),
                "median_opt": np.median(o),
                "max_opt": o.max(),
                "median_greedy": round(float(np.median(succ)), 2),
                "min_greedy": round(float(np.min(succ)), 2),
            }
        )

print(f"5 of 16 ETFs, lam={lam:g}, 64 quarterly windows (counts = windows per group)")
print(pd.DataFrame(rows).to_string(index=False))
