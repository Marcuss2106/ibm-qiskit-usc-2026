# QeMCMC portfolio search — project scope

> Current scope for the 24-hour IBM Quantum hackathon. It supersedes
> `QeMCMC_Roadmap (1).docx`, which described an earlier QeMCMC-vs-QAOA backtest design.
> Literature support and critique are in [`research/`](research/README.md).

## Research question

Can quantum circuit proposals help a search get close to the best-scoring ETF portfolio in
fewer attempts than classical swap proposals, and what does that cost in circuit shots and
runtime?

## Problem

Select exactly k of n ETFs and weight them equally. Historical adjusted daily returns give
estimates of each ETF's expected return and of how the ETFs move together. The score is
expected portfolio return minus a penalty for portfolio variance.

The original eight-ETF basket is SPY, IWM, EFA, EEM, IEF, TLT, GLD and DBC. The basket for
the larger cases, the historical windows and the risk penalty are open for discussion.

## Proposed comparison

| Component | Classical swap-based Metropolis | Quantum-assisted search |
|---|---|---|
| Proposal | Randomly exchange one held ETF for one unheld ETF. | Initialize one qubit per ETF from the current holdings. An XY circuit produces a measured bit string and, in the ideal circuit, preserves the holding count. A portfolio-score phase between mixing blocks can give the proposal information about the objective. |
| Acceptance | Score the new portfolio and apply a temperature-based Metropolis rule. | Same score and acceptance rule for feasible proposals. Wrong-count hardware outcomes count as attempts and leave the portfolio unchanged. |
| What changes next | The accepted portfolio is the next starting point; a rejection keeps the current portfolio. | Same feedback loop, with a circuit generating the next proposal. |

The intended claim is about optimization. If the quantum proposal is asymmetric, the simple
acceptance rule gives a search heuristic. Asset visit counts can describe the search;
reading them as probabilities under a target distribution would need a valid sampling scheme
and adequate mixing.

Both methods share the same data, scoring function, starting portfolios, temperature
schedule and proposal budget. Exact enumeration on the smaller cases provides an answer key.

**Main result:** best-so-far objective gap versus attempted proposals, across matched runs
and historical windows. Alongside it: success rate within budget, score evaluations and
runtime. The hardware demo reports shots, usable proposal rate and elapsed time separately.

**Ablations:** a classical multi-asset swap baseline tests whether any improvement comes
from larger moves; an XY-only circuit isolates the contribution of the score phase.

## Sizes under consideration

One qubit per candidate ETF. Valid portfolios = number of ways to choose k of n.

| Holdings | Qubits | Valid portfolios | Proposed role |
|---|---|---|---|
| 3 of 8 | 8 | 56 | Small comparison and hardware fallback |
| 4 of 12 | 12 | 495 | IBM hardware target; intermediate simulator case |
| 5 of 16 | 16 | 4,368 | Main benchmark on a 24 GB laptop, exact answer for every window |
| 6 of 20 | 20 | 38,760 | Simulator stretch if repeated circuits are fast enough |
| 8 of 24 | 24 | 735,471 | Lower-priority simulator option |
| 10 of 30 | 30 | 30,045,015 | Full-state simulation impractical (16 GiB raw statevector) |
| 10 of 50 | 50 | 10,272,278,170 | Motivation or classical-only extension; count alone does not establish hardness |

Hardware scope: a batch of proposals from a few fixed starting portfolios, paired with the
same circuits in simulation. A full adaptive hardware chain adds queue and round-trip time,
because each circuit depends on the previous measurement and acceptance decision. Compiled
depth, shot budget and usable output rate decide whether 12 qubits makes sense under the
IBM Quantum Open Plan limits.

## Questions for critique

1. Is 5 of 16 large enough to show meaningful differences in search behavior, given that
   exact enumeration is easy? How should we explain the value of the answer key to judges?
2. Would a multi-asset swap, a simple greedy search, or another classical control make the
   comparison more convincing?
3. Does the score-informed XY circuit give the quantum step a substantive role, and is there
   a simpler circuit worth considering within the time budget?
4. Is a hardware demonstration of the proposal step enough to support the pitch if the
   repeated end-to-end comparisons are simulated?
5. If the classical baseline wins, what measured result or diagnostic would still make the
   project interesting?

Answers: [`research/scope-review.md`](research/scope-review.md).

## Presentation concept

A five-minute pitch: show one classical swap and one measured quantum proposal from the same
starting portfolio, then walk through the fixed holding count and the acceptance decision.
The 16-asset chart shows how quickly each method closes the objective gap. A short hardware
panel shows whether the same proposal circuit produced usable candidates on IBM hardware.
The conclusion separates proposal efficiency from end-to-end runtime.

## References

Layden et al. on quantum-enhanced MCMC; Wang et al. on XY mixers; Marshall et al. on
quantum-assisted combinatorial optimization. Full list: [`research/references.md`](research/references.md).
