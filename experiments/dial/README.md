# Difficulty dial (bead t3h, branch `pilot/factor-selection`)

**Question.** As the portfolio landscape is made more rugged, does the quantum proposal
start to mix faster than classical proposals?

**Dial** (`qemcmc/dial.py`). Per window, remove a fraction s of the market component
(top principal component) from the real Σ: s = 0 (real data), 0.25, 0.5, 0.75, 1. Far
end, "random": real volatilities, random 3-factor correlations with no market factor.
Two objectives: mean–variance at λ = 30, and risk-only. Temperature T = τ × std(S).
Simulation only, ring XY mixer, full score phase.

**Methods** (exact spectral gaps, ratio to uniform single swap, per attempt):
multi-swap (global Kawasaki, blind long jumps); locally balanced informed swaps
(Zanella 2019, the strong classical baseline, costs k(n−k) score evaluations per
attempt); quantum proposal (best of a small β/g grid per window, so optimistic).

```bash
python -m qemcmc.dial --n 12 --k 4 --every 4                       # 16 windows, all points
python -m qemcmc.dial --n 16 --k 5 --every 16 --tau 0.1 --beta 1.0 --g 1 3 \
    --phase full --dial 0.0 1.0 random                             # 4 windows
```

## Results, 5 of 16 (τ = 0.1, 4 windows; medians)

| Objective | Dial | Local optima | Greedy success | Multi-swap | Locally balanced (per attempt) | Quantum (best) | Quantum > swap | Quantum > multi-swap |
|---|---|---|---|---|---|---|---|---|
| λ = 30 | real | 1 | 100% | 0.37 | 4.37 | 0.57 | 0% | 100% |
| risk-only | real | 1 | 100% | 0.34 | 4.57 | 0.56 | 0% | 100% |
| λ = 30 | market removed | 1 | 100% | 0.23 | 8.34 | 0.27 | 0% | 75% |
| risk-only | market removed | 3 | 43% | 0.82 | 3.27 | 0.77 | 25% | 25% |
| λ = 30 | random | 2 | 74% | 0.26 | 7.56 | 0.41 | 0% | 100% |
| risk-only | random | 12.5 | 22% | **1.19** | 3.31 | **1.10** | 75% | 25% |

4 of 12 (16 windows, every dial point, τ = 0.1 and 0.3) shows the same pattern:
quantum below swap at every real-data point (0.27–0.75), above swap only at random
risk-only (1.17 at τ = 0.1; better in 62% of windows), where multi-swap is 1.31.

Per **score evaluation**, locally balanced swaps fall to 0.06–0.15× swap at 5 of 16
(0.11–0.24× at 4 of 12): plain swap is the most efficient classical method per
evaluation everywhere.

## Conclusions

1. **The quantum proposal beats single swaps only at the far, synthetic end** (random
   correlations, risk-only, the most rugged setting: median 12.5 local optima,
   greedy success 22%). There it mixes about 1.1× faster per attempt.
2. **Even there, blind multi-swap is better** (1.19×; quantum beats it in only 25% of
   windows). The circuit's advantage is "long jumps", not "score-informed jumps".
3. **Removing the market factor alone is not enough.** At s = 1 on real data the
   quantum ratio is 0.27–0.77.
4. **Keeping returns kills the effect.** At λ = 30 the quantum proposal stays below
   swap at every dial point, including random correlations.
5. **Per attempt, the best method is classical:** locally balanced informed swaps
   (3–8× swap). They cost k(n−k) score evaluations per attempt, so per evaluation plain
   swaps win; a quantum proposal costs shots instead.

**Caveats.** 5 of 16 uses only 4 windows; the quantum grid is small (β = 1.0,
g ∈ {1, 3}) and chosen per window, which favours the quantum side; T fixed at
0.1 × std(S); no random per-step β/γ (Layden style) tested.
