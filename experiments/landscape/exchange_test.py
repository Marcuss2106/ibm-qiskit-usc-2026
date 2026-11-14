"""How close is the real objective to a valuated matroid (M-natural-concave on k-sets)?

Exchange condition: for portfolios X, Y and i in X \\ Y there is j in Y \\ X with
    f(X - i + j) + f(Y - j + i) >= f(X) + f(Y).
If it holds everywhere, any single-swap local optimum is global (Murota 2003,
Discrete Convex Analysis, ch. 6). We sample random (X, Y, i) triples and report the
violation rate for real Sigma vs. random correlations (same vols), 5 of 16.

Result (2026-11-14): about 23% violations in every case, real or random, with or
without returns. A purely linear score gives 0%, but adding tiny random noise also
gives about 23%: the exact condition is broken by any pair term, whatever its size.
So real data are NOT M-natural-concave, the theorem does not explain the single peak,
and this test cannot tell easy landscapes from hard ones. The single peak is a
quantitative effect (node terms dominate; the market factor makes pairs substitutes).
"""
import numpy as np

from qemcmc import data
from qemcmc.objective import enumerate_scores
from qemcmc.states import StateSpace

n, k = 16, 5
sp = StateSpace(n, k)
rng = np.random.default_rng(0)
SAMPLES = 20000
TOL = 1e-12


def violation_rate(scores):
    bad = tested = 0
    for _ in range(SAMPLES):
        a, b = rng.choice(sp.size, 2, replace=False)
        X, Y = set(sp.combos[a]), set(sp.combos[b])
        only_x, only_y = sorted(X - Y), sorted(Y - X)
        i = only_x[rng.integers(len(only_x))]
        base = scores[a] + scores[b]
        ok = False
        for j in only_y:
            x2 = sp.rank_of_combo(sorted(X - {i} | {j}))
            y2 = sp.rank_of_combo(sorted(Y - {j} | {i}))
            if scores[x2] + scores[y2] >= base - TOL:
                ok = True
                break
        bad += not ok
        tested += 1
    return bad / tested


z = data.load_instances(16)
windows = range(0, 64, 8)  # 8 windows spread over 2010-2025


def random_sigma(w, m):
    vol = np.sqrt(np.diag(z["Sigma"][w]))
    A = rng.normal(size=(n, 3))
    A[:, 0] += m
    C = A @ A.T + np.diag(rng.uniform(0.1, 0.5, n))
    d = np.sqrt(np.diag(C))
    return C / np.outer(d, d) * np.outer(vol, vol)


cases = {
    "real, lam=3": lambda w: enumerate_scores(sp, z["mu"][w], z["Sigma"][w], 3.0),
    "real, risk-only": lambda w: enumerate_scores(sp, np.zeros(n), z["Sigma"][w], 1.0),
    "random corr (no market), risk-only": lambda w: enumerate_scores(sp, np.zeros(n), random_sigma(w, 0.0), 1.0),
    "random corr (market m=2), risk-only": lambda w: enumerate_scores(sp, np.zeros(n), random_sigma(w, 2.0), 1.0),
}
for name, f in cases.items():
    rates = [violation_rate(f(w)) for w in windows]
    print(f"{name:38s} exchange violations: median {np.median(rates):6.2%}  max {np.max(rates):6.2%}")
