"""Control for mixer_test.py: is the complete-mixer gain from the score phase?

Same complete-mixer circuit with the score phase switched off (phase "none": a
structured random jump) vs. with the full phase, 6 long / 6 short, all 64 windows.
Same beta grid; tuned multi-swap for reference. Run from the repo root:
    PYTHONPATH=. python experiments/longshort/phase_control.py
"""
import numpy as np
import pandas as pd

from qemcmc import data
from qemcmc.longshort import longshort_scores, longshort_terms, stock_windows
from qemcmc.subspace import _space, mixer_matrix, multiswap_table, proposal_table_fast, spectral_gap, swap_table

N, NV, KV, TAU = 12, 11, 5, 0.1
BETAS = (0.1, 0.2, 0.3, 0.5, 0.75, 1.0)


def run(name, sigmas):
    sp = _space(NV, KV)
    Qs = swap_table(sp)
    Qm = {m: multiswap_table(sp, m) for m in range(2, KV + 1)}
    A = {be: mixer_matrix(NV, KV, be, "complete") for be in BETAS}
    rows = []
    for w in range(64):
        sig = sigmas[w][:N, :N]
        S = longshort_scores(sp, sig)
        T = TAU * S.std()
        h, J = longshort_terms(sig)
        gs = spectral_gap(Qs, S, T)
        none = max(spectral_gap(proposal_table_fast(NV, KV, h, J, be, 0.0, "complete", "none", A=A[be]), S, T)
                   for be in BETAS) / gs
        full = max(spectral_gap(proposal_table_fast(NV, KV, h, J, be, g / S.std(), "complete", "full", A=A[be]), S, T)
                   for be in BETAS for g in (1.0, 3.0)) / gs
        multi = max(spectral_gap(Qm[m], S, T) for m in Qm) / gs
        rows.append({"universe": name, "w": w, "no_phase": none, "full_phase": full, "multi_tuned": multi})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = pd.concat([run("ETFs", data.load_instances(20)["Sigma"]), run("stocks", stock_windows())])
    out.to_csv(data.ROOT / "results" / "longshort_phase_control_n12.csv", index=False)
    for name, d in out.groupby("universe", sort=False):
        print(f"{name:6s} complete mixer, no phase {d.no_phase.median():.2f} | full phase {d.full_phase.median():.2f} "
              f"| tuned multi-swap {d.multi_tuned.median():.2f}   "
              f"no-phase > multi {(d.no_phase > d.multi_tuned).mean():.0%}   "
              f"full > no-phase {(d.full_phase > d.no_phase).mean():.0%} "
              f"(median gain {np.median(d.full_phase / d.no_phase):.2f}x)")
