"""Direct race: attempts and score evaluations to first reach the optimum S*.

6 long / 6 short (default; --n 16 for 8 long / 8 short on 8 test windows), the
held-out test windows from fair_tuning.py, ETFs and stocks.
40 random starting books per window, identical across methods. Budget 3,000 attempts
per run (parallel tempering: summed over replicas). Settings fixed per method as chosen
on the train windows in fair_tuning.py. Chains are simulated exactly from each method's
transition matrix (quantum proposals sampled from the exact proposal table).

Cost per attempt in score evaluations: 1 for swap, multi-swap, quantum (plus a circuit
run) and each parallel-tempering replica step; k(n-k) = 30 for locally balanced.

Run from the repo root:
    PYTHONPATH=. python experiments/longshort/race.py
"""
import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.longshort import longshort_scores, longshort_terms, stock_windows
from qemcmc.subspace import (
    _space, informed_matrix, metropolis_matrix, mixer_matrix, multiswap_table,
    proposal_table_fast, swap_table,
)

import sys

N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 12
NV, KV, TAU = N - 1, N // 2 - 1, 0.1
BUDGET = 3000 if N == 12 else 15000
STARTS = 40 if N == 12 else 24
WINDOWS = range(1, 64, 2) if N == 12 else range(1, 64, 8)  # all test windows / 8 of them
PT_TEMPS = np.geomspace(1.0, 10.0, 4)  # multiples of T: T, 2.2T, 4.6T, 10T
EVALS = {"single swap": 1, "multi-swap": 1, "locally balanced": KV * (NV - KV),
         "parallel tempering": 1, "quantum complete+full": 1}


def chosen_settings():
    df = pd.read_csv(data.ROOT / "results" / "longshort_fair_tuning_n12.csv")
    out = {}
    for uni, d in df.groupby("universe"):
        tr = d[d.w % 2 == 0]
        best = tr.groupby(["method", "setting"]).ratio.median().groupby(level=0).idxmax()
        out[uni] = {m: s for m, s in best}
    return out


def first_hit(P, starts, target, rng, budget=BUDGET):
    """Attempts until each chain first sits on `target` (budget + 1 if never)."""
    cum = np.cumsum(P, axis=1)
    s = starts.copy()
    hit = np.where(s == target, 0, budget + 1)
    for t in range(1, budget + 1):
        live = hit > budget
        if not live.any():
            break
        u = rng.random(live.sum())
        s[live] = (cum[s[live]] < u[:, None]).sum(axis=1).clip(max=P.shape[0] - 1)
        hit[live & (s == target)] = t
    return hit


def pt_first_hit(S, T, starts, target, rng, budget=BUDGET):
    """Parallel tempering with single-swap Metropolis replicas and adjacent exchanges.
    One sweep = one attempt per replica; budget counts replica attempts."""
    sp = _space(NV, KV)
    Ps = [np.cumsum(metropolis_matrix(swap_table(sp), S, T * f), axis=1) for f in PT_TEMPS]
    R, C = len(PT_TEMPS), len(starts)
    s = np.tile(starts, (R, 1))  # all replicas start at the same book
    hit = np.where(starts == target, 0, budget + 1)
    attempts = 0
    while attempts < budget:
        for r in range(R):
            u = rng.random(C)
            s[r] = (Ps[r][s[r]] < u[:, None]).sum(axis=1).clip(max=len(S) - 1)
            attempts += 1
            newly = (hit > budget) & (s[r] == target)
            hit[newly] = attempts
        for r in range(R - 1):  # exchange adjacent temperatures
            b1, b2 = 1 / (T * PT_TEMPS[r]), 1 / (T * PT_TEMPS[r + 1])
            acc = np.minimum(1, np.exp((b1 - b2) * (S[s[r + 1]] - S[s[r]])))
            sw = rng.random(C) < acc
            s[r, sw], s[r + 1, sw] = s[r + 1, sw], s[r, sw]
    return hit


def race(name, sigmas, settings):
    sp = _space(NV, KV)
    m = int(settings["multi-swap"].split("=")[1])
    qb, qg = (float(x.split("=")[1]) for x in settings["complete+full"].split(","))
    A = mixer_matrix(NV, KV, qb, "complete")
    rows = []
    for w in WINDOWS:
        sig = sigmas[w][:N, :N]
        S = longshort_scores(sp, sig)
        T = TAU * S.std()
        h, J = longshort_terms(sig)
        target = int(S.argmax())
        rng = np.random.default_rng(1000 + w)
        starts = rng.integers(0, sp.size, STARTS)
        Pq = metropolis_matrix(proposal_table_fast(NV, KV, h, J, qb, qg / S.std(), "complete", "full", A=A), S, T)
        chains = {
            "single swap": metropolis_matrix(swap_table(sp), S, T),
            "multi-swap": metropolis_matrix(multiswap_table(sp, m), S, T),
            "locally balanced": informed_matrix(sp, S, T),
            "quantum complete+full": Pq,
        }
        for meth, P in chains.items():
            hits = first_hit(P, starts, target, np.random.default_rng(w))
            rows += [{"universe": name, "w": w, "method": meth, "attempts": a} for a in hits]
        hits = pt_first_hit(S, T, starts, target, np.random.default_rng(w))
        rows += [{"universe": name, "w": w, "method": "parallel tempering", "attempts": a} for a in hits]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    sets = chosen_settings()
    df = pd.concat([race("ETFs", data.load_instances(20)["Sigma"], sets["ETFs"]),
                    race("stocks", stock_windows(), sets["stocks"])])
    df["evals"] = df.attempts * df.method.map(EVALS)
    df["solved"] = df.attempts <= BUDGET
    df.to_csv(data.ROOT / "results" / f"longshort_race_n{N}.csv", index=False)
    for uni, d in df.groupby("universe", sort=False):
        print(f"\n== {uni}: {N // 2} long / {N // 2} short, {len(WINDOWS)} test windows x {STARTS} starts, budget {BUDGET} attempts")
        g = d.groupby("method")
        tab = pd.DataFrame({
            "solved": g.solved.mean(),
            "median attempts": g.attempts.median(),
            "mean attempts (unsolved=budget)": g.attempts.apply(lambda a: np.minimum(a, BUDGET).mean()),
            "median score evals": g.evals.median(),
        }).sort_values("median attempts")
        print(tab.round(2).to_string())
