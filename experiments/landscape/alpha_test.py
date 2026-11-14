"""SPY-hedged mean-variance: S(x) = alpha.x/k - lam/k^2 x' Sigma_res x.

Residual return of ETF i: r_i - beta_i * r_SPY (beta estimated in-window).
An equal-weight k-ETF portfolio hedged with SPY at its average beta earns
exactly the average residual, so the objective keeps the same quadratic form.
SPY is the hedge, so the 16 selectable assets are TICKERS[1:17].
"""
import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

n, k = 16, 5
sp = StateSpace(n, k)
nb = sp.swap_neighbors()
r = data.daily_returns(data.clean_prices(data.load_prices()))
assets = data.TICKERS[1:17]
ends = data.quarter_ends()


def windows(hedged: bool):
    out = []
    for q in ends:
        w = r.loc[:q].iloc[-252:]
        X = w[assets].to_numpy()
        if hedged:
            m = w["SPY"].to_numpy()
            mc = m - m.mean()
            beta = (X - X.mean(0)).T @ mc / (mc @ mc)
            X = X - np.outer(m, beta)
        out.append((252 * X.mean(0), 252 * np.cov(X, rowvar=False)))
    return out


def ring_capture(S):
    """Share of total |off-diagonal| weight on a greedy max-weight ring."""
    A = np.abs(S - np.diag(np.diag(S)))
    order, left = [0], set(range(1, n))
    while left:
        nxt = max(left, key=lambda j: A[order[-1], j])
        order.append(nxt)
        left.remove(nxt)
    ring = sum(A[order[i], order[(i + 1) % n]] for i in range(n))
    return ring / (A.sum() / 2)


rows = []
for hedged in [False, True]:
    W = windows(hedged)
    risk_opt = [enumerate_scores(sp, np.zeros(n), S, 1.0).argmax() for _, S in W]
    for lam in [1, 3, 10, 30, 100]:
        opts, succ, best, ret_matters = [], [], [], []
        for (mu, S), ro in zip(W, risk_opt):
            sc = enumerate_scores(sp, mu, S, lam)
            opts.append(local_optima(sc, nb).sum())
            succ.append((greedy_endpoints(sc, nb) == sc.argmax()).mean())
            best.append(sc.argmax())
            ret_matters.append(sc.argmax() != ro)
        o = np.array(opts)
        rows.append(
            {
                "objective": "SPY-hedged" if hedged else "plain",
                "lam": lam,
                "win>1": f"{np.mean(o > 1):.0%}",
                "win>5": f"{np.mean(o > 5):.0%}",
                "med_opt": np.median(o),
                "max_opt": o.max(),
                "greedy": round(float(np.median(succ)), 2),
                "distinct_opt": len(set(best)),
                "return_changes_opt": f"{np.mean(ret_matters):.0%}",
            }
        )
    cap = np.median([ring_capture(S) for _, S in W])
    rows[-1]["ring_capture"] = f"{cap:.0%}"

print(pd.DataFrame(rows).fillna("").to_string(index=False))
