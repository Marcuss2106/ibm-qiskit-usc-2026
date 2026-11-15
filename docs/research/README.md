# Research — QeMCMC portfolio search

Supporting research for [`../project-scope.md`](../project-scope.md): can count-preserving
quantum circuit proposals find the best equal-weight ETF portfolio in fewer attempts than
classical swap proposals, and at what cost in shots and runtime?

`../QeMCMC_Roadmap (1).docx` describes an earlier design (QeMCMC vs. QAOA with a monthly
backtest) and is kept for history only. `../Quantum_Optimization_Study_Guide.pdf` remains
useful background.

| File | What it is |
|---|---|
| [`scope-review.md`](scope-review.md) | Answers to the scope's five critique questions; keep/change/drop; sizing and hardware budget |
| [`literature-review.md`](literature-review.md) | Thematic synthesis, each section ending in implications for the build |
| [`rugged-landscapes.md`](rugged-landscapes.md) | Why every window is single-peaked; finance problems with exactly k holdings that can be rugged; tuning knobs, screen, baselines, experiments E0–E7 |
| [`longshort-complete-mixer.md`](longshort-complete-mixer.md) | Testing so far on the 6 long / 6 short ETF book: complete-mixer quantum proposal vs classical baselines, tests 1–6 and current claim |
| [`presentation-reference.md`](presentation-reference.md) | How to build the talk: 3Blue1Brown-style explanation, slide research (Alley, Mayer, Doumont), Winston's speaking techniques, manim-slides patterns, draft QeMCMC outline |
| [`references.md`](references.md) | Annotated bibliography: DOI, OpenAlex ID, peer-review status, depth read |
| [`references.bib`](references.bib) | BibTeX for the same works |

## Summary

**The design is well grounded.** The classical swap move is Kawasaki dynamics, the standard
count-preserving MCMC move. Count-preserving XY circuits are established (Hadfield 2019,
Wang 2020) and have run on hardware for portfolio problems (He 2023). The closest prior work,
Kawamata et al. (2026), already uses XY-mixer circuits to build count-preserving MCMC
proposals. They benchmark against local and global Kawasaki dynamics and demonstrate it on
an IBM Heron processor. The project should cite it as the nearest neighbor and differ by
using direct per-step circuit proposals on real financial data, with an exact answer key.

**Main recommendations** (details in [`scope-review.md`](scope-review.md)):

1. **Check the landscape first.** Count local optima under swaps for every window. If most
   windows have one optimum, no proposal can beat simple descent by much; adjust λ or the
   basket.
2. **Add an informed classical control.** The score-informed circuit uses objective
   information, so compare it with heat-bath swaps and greedy search with restarts, not
   just blind swaps. Report score evaluations alongside attempts.
3. **Make the circuit palindromic** (mix, score phase, reversed mix). Proposals are then
   symmetric and the Metropolis rule is valid, so the search is a correct sampler rather
   than only a heuristic.
4. **Precompute proposal tables** up to 16 assets: one simulation per valid portfolio, then
   chains are table lookups and spectral gaps are exact. Promote 6 of 20 to a secondary
   benchmark; drop 10 of 30 as a simulator case.
5. **On hardware, measure a full proposal table at 4 of 12** (495 starts in one batch) and
   replay the search offline with hardware-drawn proposals. Use a ring XY mixer and a
   score phase with single-asset terms only to keep depth low. The IBM Open Plan allows
   10 QPU-minutes per 28-day window, so pilot the shot cost first.
6. **Plan for classical to win.** Jump-distance profiles, an evolution-time sweep, exact
   spectral gaps and hardware fidelity keep a negative result informative.

**Update after the landscape check** (details in [`rugged-landscapes.md`](rugged-landscapes.md)).
Every window turned out single-peaked, which is the expected result: per-asset terms are
about 13× the pair terms, and a near-additive score over exactly k assets has one swap
optimum. Removing the market mode is a weak dial, because a shared market factor adds the
same amount to every 5-asset portfolio. The main dial is r, the spread of pair terms over
the spread of per-asset terms. Candidates in order: minimum variance on a mixed-asset
universe, market-neutral long/short with fixed counts, least-correlated k, and credit
feature selection. Screen each instance (at least 3 swap optima, global basin under 30%)
before running QeMCMC, and add parallel tempering and a classically simulated quantum
proposal as baselines.

## Discovery log

- OpenAlex API: keyword searches, DOI lookups, and forward-citation graphs (works citing
  Layden 2023, Marshall 2026 and Wang 2020). New for this scope: Kawasaki dynamics, swap
  heuristics for cardinality-constrained portfolios, and count-preserving QeMCMC.
- Rugged-landscape follow-up (November 2026): four parallel literature searches covering
  QeMCMC advantage conditions, rugged portfolio formulations, banking selection problems and
  ruggedness metrics. Notes are in `../../research_notes/QeMCMC rugged finance landscapes/`
  and the full report in `../../reports/QeMCMC rugged finance landscapes.md`. OpenAlex IDs
  for five of the new references are missing because the daily OpenAlex limit was reached.
- Full text read: Layden et al. 2023 (arXiv:2203.12497) and Marshall et al. 2026
  (arXiv:2602.06171v2). Everything else is abstract or metadata only, as flagged in
  `references.md`.
- IBM Quantum Open Plan limits read from the IBM Quantum Platform docs (plans overview and
  instances guide), November 2026: "10 minutes of quantum processing unit (QPU) usage per
  28-day rolling window." Which execution modes the Open Plan allows was not stated on the
  pages read; check before planning a session.
