# Project glossary

Plain-language definitions for the portfolio, sampling, and quantum-computing terms
used in this project. For methods and results, see the [project overview](../README.md),
[research results](../research_results.md), and [development guide](DEVELOPMENT.md).

## Portfolios and data

- **ETF (exchange-traded fund):** A fund traded on an exchange like a stock. The
  project uses historical ETF prices to construct portfolio problems.
- **Portfolio / book:** A set of asset positions. The original problem selects
  exactly `k` of `n` assets with equal positive weights. The main long–short problem
  holds every asset and chooses which half to hold long and which half short.
- **Long / short:** A long position gains when an asset's price rises; a short
  position gains when it falls. In the long–short model, the position signs are
  `+1` and `-1`, with weights of `+1/n` and `-1/n`.
- **Market-neutral book:** Here, an equal-size long–short portfolio whose weights
  sum to zero. This balances long and short dollar exposure; it does not guarantee
  zero exposure to market movements.
- **Mean return (`mu` or μ):** The average asset return estimated from a data window
  and annualized. It supplies the return term in the original objective.
- **Covariance matrix (`Sigma` or Σ):** A table describing how asset returns vary
  together. Its diagonal entries are individual return variances. The project uses
  it to calculate portfolio risk as the variance `wᵀ Sigma w`, where `w` is the
  vector of portfolio weights.
- **Window / instance:** One portfolio problem built from a historical data window.
  The main dataset uses the last 252 trading-day returns on or before each quarter
  end, giving 64 windows from 2010 through 2025.

## States and objectives

- **State / valid portfolio:** A portfolio encoded as a bit string with a fixed
  number of ones. In the original problem, a one means an asset is selected. In
  the long–short implementation, asset 0 is fixed long to avoid counting a book and
  its sign-reversed copy twice; the remaining bits identify the other long assets.
- **State space / rank:** The collection of valid states, and the integer index
  assigned to each by `StateSpace`. Proposal tables and chains use these ranks to
  refer to portfolios consistently.
- **Score / objective (`S`):** The number the search tries to maximize. The original
  score balances mean return against variance using a risk penalty `lambda` (λ).
  The long–short score is negative portfolio variance, so a higher score means less
  risk. Energy uses the opposite sign: `E = -S`.
- **Answer key / global optimum (`S*`):** The largest score across all valid states,
  found by enumerating them. More than one portfolio can have this score.
- **Score gap:** `S* - best score found so far`. Zero means the search has found a
  global optimum. Smaller is better; this differs from the spectral gap below.
- **Swap / swap neighbor:** A move that exchanges one one-bit and one zero-bit,
  preserving the count. It replaces one selected asset in the original problem,
  or exchanges a long and a short among the unfixed assets in the long–short model.
- **Multi-swap:** A proposal that exchanges several one-bits with the same number
  of zero-bits. The classical implementation chooses a swap count uniformly from
  one up to a chosen maximum, then chooses a state at that swap distance uniformly.
- **Local optimum / rugged landscape:** A local optimum has no single-swap neighbor
  with a higher score. A rugged landscape has multiple such peaks, so improving
  swaps alone can stop before reaching the global optimum.

## Sampling and search

- **MCMC (Markov chain Monte Carlo):** Sampling by repeatedly updating a state using
  a rule that depends on the current state. Here, each update proposes a portfolio
  and then accepts it or keeps the current portfolio.
- **Proposal table (`Q`):** A matrix where `Q[s, s']` is the probability of proposing
  state `s'` from state `s`, before the acceptance decision.
- **Metropolis acceptance:** For a symmetric proposal, accept a proposed state with
  probability `min(1, exp((S(new) - S(current)) / T))`. Improving moves are always
  accepted; worse moves can also be accepted, helping the chain leave local peaks.
- **Temperature (`T`):** A positive parameter controlling how strongly the chain
  favors higher scores. Lower temperatures make score-decreasing moves less likely.
- **Target distribution:** The intended long-run sampling probabilities, here
  proportional to `exp(S / T)`. Higher-scoring portfolios receive more probability,
  but sampling this distribution differs from finding only the best portfolio.
- **Transition matrix (`P`):** The probabilities of the chain's actual next state
  after proposal and acceptance. Rejected proposals add probability to staying in
  the current state, so `P` generally differs from `Q`.
- **Mixing / spectral gap:** Mixing is convergence toward the target distribution.
  The code measures the absolute spectral gap: one minus the second-largest
  eigenvalue magnitude of `P`. Larger gaps indicate faster asymptotic mixing per
  attempt; they do not by themselves establish faster optimization or lower runtime.
- **Gap ratio:** In the reported sampling comparisons, a method's spectral gap
  divided by single-swap Metropolis's gap for the same instance and temperature.
  A ratio above one favors that method on this mixing measure.
- **Attempt / score evaluation:** An attempt is one proposal, accepted or rejected.
  A score evaluation computes the objective for a portfolio. These are separate
  costs: a method may evaluate several neighbors to make one proposal. Hardware
  outcomes with an invalid count still count as attempts and leave the state unchanged.
- **Held-out windows:** Windows reserved for evaluation after method settings have
  been chosen on other windows. This tests whether settings work beyond the tuning
  data; it does not measure future investment performance.

## Quantum proposals and hardware

- **QeMCMC (quantum-enhanced MCMC):** MCMC whose proposal comes from a quantum
  circuit. The accept-or-reject decision remains classical in this project.
- **Qubit / computational basis state:** A qubit is the basic unit of a quantum
  circuit. A computational basis state encodes a definite bit string, such as the
  current portfolio, before the circuit creates a superposition of possible outcomes.
- **XY mixer:** Gates that exchange `01` and `10` components while preserving the
  total number of ones. A ring mixer couples adjacent qubits on a ring; a complete
  mixer includes every pair. The mixing angle `beta` (β) controls these rotations.
- **Score phase:** A diagonal circuit block that changes phases according to score
  information, with strength controlled by `gamma` (γ). A subsequent mixer turns
  phase differences into changes in measurement probabilities. The full phase uses
  all pairwise score terms; the phase-off control removes this block's effect.
- **Palindromic circuit / symmetric proposal:** The circuit applies a mixer, a
  score phase, then the same mixer gates in reverse order. For the ideal gates used
  here, this makes `Q[s, s'] = Q[s', s]`, allowing plain Metropolis acceptance.
  Hardware noise can break that symmetry.
- **Shot / usable rate:** A shot is one circuit execution and measurement. The
  usable rate is the fraction of measured outcomes with the required number of
  ones. Ideal circuits preserve that count, but hardware noise can change it.
- **Subspace simulation:** Classical simulation restricted to valid states with
  the required count, rather than all possible bit strings. It reduces simulation
  cost while reproducing the ideal count-preserving circuit.
- **Transpilation / two-qubit gate count:** Transpilation translates a circuit into
  gates and qubit connections supported by a device. The resulting two-qubit gate
  count measures part of the hardware cost; it is distinct from circuit depth,
  shots, and elapsed time.
