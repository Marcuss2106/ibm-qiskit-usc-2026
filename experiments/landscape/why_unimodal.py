"""Separate data vs. methodology causes of the single-peak landscape (5 of 16)."""
import numpy as np

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

n, k = 16, 5
sp = StateSpace(n, k)
nb = sp.swap_neighbors()


def stats(mus, sigmas, lam):
    opts, succ = [], []
    for mu, S in zip(mus, sigmas):
        s = enumerate_scores(sp, mu, S, lam)
        opts.append(local_optima(s, nb).sum())
        succ.append((greedy_endpoints(s, nb) == s.argmax()).mean())
    o = np.array(opts)
    return (
        f"median opt {np.median(o):3.0f}  max {o.max():3d}  "
        f"windows>1: {np.mean(o > 1):4.0%}  median greedy success {np.median(succ):.2f}"
    )


z = data.load_instances(16)
rows = {}
for lam in [3, 1e5]:
    rows[f"real data, lam={lam:g}"] = stats(z["mu"], z["Sigma"], lam)

# Same real mu and volatilities; correlations replaced by a random 3-factor model
rng = np.random.default_rng(0)
mus, sig = [], []
for w in range(64):
    vol = np.sqrt(np.diag(z["Sigma"][w]))
    A = rng.normal(size=(n, 3))
    C = A @ A.T + np.diag(rng.uniform(0.1, 0.5, n))
    d = np.sqrt(np.diag(C))
    C = C / np.outer(d, d)
    mus.append(z["mu"][w])
    sig.append(C * np.outer(vol, vol))
for lam in [3, 1e5]:
    rows[f"random correlations, lam={lam:g}"] = stats(mus, sig, lam)

# Real data with the last two of 16 replaced by synthetic inverse SPY and inverse TLT
r = data.daily_returns(data.clean_prices(data.load_prices()))[data.TICKERS[:16]].copy()
r["XLV"] = -r["SPY"]
r["EWJ"] = -r["TLT"]
_, mu2, S2 = data.window_estimates(r)
for lam in [3, 1e5]:
    rows[f"real + inverse SPY/TLT, lam={lam:g}"] = stats(mu2, S2, lam)

for name, v in rows.items():
    print(f"{name:34s} {v}")
