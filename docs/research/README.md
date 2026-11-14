# Research synthesis — QeMCMC portfolio selection

Supporting literature for [`../QeMCMC_Roadmap (1).docx`](../) and
[`../Quantum_Optimization_Study_Guide.pdf`](../Quantum_Optimization_Study_Guide.pdf).
Discovery was done with the OpenAlex API (searches, DOI lookups, and forward-citation
graphs of Layden 2023 and Marshall 2026) on 2026-11-14; the two core QeMCMC papers were
read in full text on arXiv.

| File | What it is |
|---|---|
| [`literature-review.md`](literature-review.md) | Thematic synthesis, each section ending in "Implication for our build" |
| [`roadmap-design-notes.md`](roadmap-design-notes.md) | Every roadmap parameter/decision → literature support, risk, suggested check |
| [`references.md`](references.md) | Annotated bibliography with DOI, OpenAlex ID, peer-review status, depth read |
| [`references.bib`](references.bib) | BibTeX for the same works |

## The shared objective

Both methods minimize the same function over 8 binary asset choices x, with budget B = 3
and equal weights w = x / B:

$$
F(x) = \frac{\lambda}{B^2}\, x^\top \Sigma x \;-\; \frac{1}{B}\, \mu^\top x \;+\; \rho \Big(\sum_i x_i - B\Big)^2
$$

That gives 2⁸ = 256 states, of which C(8, 3) = 56 are feasible portfolios.

## Summary

The project's QUBO — choose 3 of 8 ETFs with a mean–variance objective plus a cardinality
penalty — is a textbook instance of the formulations in Lucas (2014), Glover et al.
(2019/2022) and the QAOA portfolio benchmark of Brandhofer et al. (2022).

**The roadmap's QeMCMC is the Layden et al. (2023, *Nature*) algorithm, not the Marshall
et al. (2026) variant.** Symmetric proposals from a cost-plus-X-mixer evolution, one shot
per proposal, plain Metropolis acceptance and a single temperature are all Layden's design.
Marshall et al. deliberately drop symmetry (first-order Trotter, warm-started Ry state,
10k-shot low-energy filtering, 5-replica parallel tempering) and call their method "purely a
heuristic."

Critiques matter for how results are framed. Orfi & Sels (2024) prove no speedup over
classical sampling for worst-case unstructured problems, and Hellstern et al. (2026) find
classical solvers (branch-and-cut, simulated annealing, parallel tempering) highly
competitive while LR-QAOA gave no quality improvement. With 8 qubits every state can be
enumerated, so the scientific content of the project is **a fair, fully-accounted comparison
on a real financial pipeline**, not a speed claim.

The two largest technical risks the literature points to:

1. **Penalty sizing.** A large ρ distorts the landscape QAOA sees and, through Layden's α
   normalization, shrinks the objective's influence on QeMCMC proposals.
2. **Low feasible fraction for X-mixer QAOA.** Only 56 / 256 ≈ 22 % of the initial state is
   feasible. Constraint-preserving alternatives (XY mixers and Dicke states: Hadfield 2019,
   Wang 2020, Bärtschi & Eidenbenz 2019, Mancilla 2026) are the natural extension.

On the finance side, DeMiguel et al. (2009) argue the equal-weight 1/N portfolio belongs in
the scorecard, Chopra & Ziemba (1993) and Merton (1980) warn that expected-return estimates
dominate the error, and Bailey & López de Prado (2014, 2016) explain why a 24-month holdout
cannot support performance claims.

## Discovery log

- OpenAlex queries via `api.openalex.org/works?search=…`, `works/doi:…`, and `filter=cites:W4384009058` / `cites:W7128371520`.
- Forward citations of Layden 2023: 104 works (most tangential); of Marshall 2026: 9 (mainly 2026 preprints on warm-starting and noise-directed QAOA).
- Full text read: Layden et al. 2023 (arXiv:2203.12497, HTML partial) and Marshall et al. 2026 (arXiv:2602.06171v2 HTML). All other entries are abstract or metadata only, as flagged in `references.md`.
