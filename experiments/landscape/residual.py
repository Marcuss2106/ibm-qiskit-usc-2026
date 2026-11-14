"""Real data with the market factor removed: Sigma minus its top principal component.

Residual (market-neutral) covariance is a standard object (idiosyncratic risk).
Usage: residual.py <stock_prices.csv>
"""
import sys

import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

n, k = 16, 5
sp = StateSpace(n, k)
nb = sp.swap_neighbors()


def residual(S, drop=1):
    w, v = np.linalg.eigh(S)
    top = v[:, -drop:]
    return S - top @ np.diag(w[-drop:]) @ top.T


def run(name, mu, sigmas):
    for drop in [0, 1, 2]:
        for lam, a in [(3, 0.0), (3, 1.0)]:
            opts, succ = [], []
            for m, S in zip(mu, sigmas):
                m = m.mean() + (1 - a) * (m - m.mean())
                sc = enumerate_scores(sp, m, residual(S, drop) if drop else S, lam)
                opts.append(local_optima(sc, nb).sum())
                succ.append((greedy_endpoints(sc, nb) == sc.argmax()).mean())
            o = np.array(opts)
            label = "risk-only" if a == 1 else f"lam={lam}"
            print(
                f"{name:6s} drop top {drop} PC  {label:9s}  windows>1 {np.mean(o > 1):4.0%}  "
                f">5 {np.mean(o > 5):4.0%}  median opt {np.median(o):3.0f}  "
                f"median greedy {np.median(succ):.2f}"
            )


z = data.load_instances(16)
run("ETFs", z["mu"], z["Sigma"])
prices = pd.read_csv(sys.argv[1], index_col="date", parse_dates=True)
_, mu, S = data.window_estimates(data.daily_returns(data.clean_prices(prices)))
run("stocks", mu, S)
