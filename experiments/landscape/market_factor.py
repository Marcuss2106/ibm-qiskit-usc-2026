"""Does a common positive market factor explain the single-peak landscape?

Random 3-factor correlations (risk-only, 5 of 16, real ETF vols), with the first
factor's loadings shifted to mean m: m=0 is the earlier 'random' control; larger
m adds a market factor that makes most pairs positively correlated.
"""
import numpy as np

from qemcmc import data
from qemcmc.landscape import greedy_endpoints, local_optima
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

n, k = 16, 5
sp = StateSpace(n, k)
nb = sp.swap_neighbors()
z = data.load_instances(16)
iu = np.triu_indices(n, 1)


def corr_of_real(S):
    d = np.sqrt(np.diag(S))
    return S / np.outer(d, d)


real_neg = np.mean([(corr_of_real(S)[iu] < 0).mean() for S in z["Sigma"]])
real_mean = np.mean([corr_of_real(S)[iu].mean() for S in z["Sigma"]])
print(f"real ETFs:          negative pairs {real_neg:4.0%}  mean corr {real_mean:+.2f}")

for m in [0.0, 0.5, 1.0, 2.0]:
    rng = np.random.default_rng(0)
    opts, succ, neg, mc = [], [], [], []
    for w in range(64):
        vol = np.sqrt(np.diag(z["Sigma"][w]))
        A = rng.normal(size=(n, 3))
        A[:, 0] += m
        C = A @ A.T + np.diag(rng.uniform(0.1, 0.5, n))
        d = np.sqrt(np.diag(C))
        C = C / np.outer(d, d)
        neg.append((C[iu] < 0).mean())
        mc.append(C[iu].mean())
        sc = enumerate_scores(sp, np.zeros(n), C * np.outer(vol, vol), 1.0)
        opts.append(local_optima(sc, nb).sum())
        succ.append((greedy_endpoints(sc, nb) == sc.argmax()).mean())
    print(
        f"random, market m={m:3.1f}: negative pairs {np.mean(neg):4.0%}  mean corr {np.mean(mc):+.2f}"
        f"  median opt {np.median(opts):4.0f}  median greedy {np.median(succ):.2f}"
    )
