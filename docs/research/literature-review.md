# Literature review

Literature behind [`../project-scope.md`](../project-scope.md): swap-based classical search
versus count-preserving quantum proposals for choosing k of n ETFs.

Citations use (Author Year); full entries are in [`references.md`](references.md).
**[full]** = read in full text; **[abs]** = claim taken from the abstract;
**[meta]** = cited for its well-known standard content, not re-read here.

## The objective

Both methods search over bit strings x with exactly k ones (one bit per ETF) and equal
weights w = x / k. With estimated annual mean returns μ, covariance Σ and risk penalty λ, the
score to maximize is:

$$
S(x) = \frac{1}{k}\, \mu^\top x \;-\; \frac{\lambda}{k^2}\, x^\top \Sigma x ,
\qquad \sum_i x_i = k
$$

The MCMC energy is its negative, E(x) = −S(x). A proposal from x to x′ is accepted with the
Metropolis probability:

$$
A(x \to x') = \min\!\Big(1,\; e^{-\left(E(x') - E(x)\right)/T}\Big)
$$

Because every proposal keeps exactly k holdings, no count penalty is needed. That removes
the penalty-tuning problem of the earlier design.

---

## 1. Classical count-preserving search

**Swap moves are Kawasaki dynamics.** Exchanging one held asset for one unheld asset is
the classical spin-exchange move introduced by Kawasaki (1966) [meta] for fixed-magnetization
Ising models; the bit-string version is the same thing. Recent quantum-MCMC papers use it as
the standard baseline for fixed-count problems. Kawamata, Nakano & Fujii (2026) [abs] compare
against "local and global Kawasaki dynamics" — one swap per step versus many.

**Swap-based portfolio heuristics are well established.** Chang, Meade, Beasley & Sharaiha
(2000) [meta] is the classic study of cardinality-constrained mean–variance portfolios,
comparing genetic algorithms, tabu search and simulated annealing. Crama & Schyns (2003)
[meta] apply simulated annealing with swap-type moves to realistic portfolio constraints.
Graham & Craven (2020) [abs] give an exact method for small cardinalities and observe that
the pieces of the efficient frontier "correspond closely to local optima" of an evolutionary
search. Local optima are a real feature of these problems, but how many there are depends on
the data.

**General MCMC tools.** The acceptance rule is Metropolis et al. (1953) [meta]; Hastings
(1970) [meta] adds the correction needed for asymmetric proposals. Simulated annealing
(Kirkpatrick et al. 1983) [meta] and parallel tempering (Earl & Deem 2005) [meta] are the
standard temperature strategies.

### Implication for our build

- Name the baseline "swap Metropolis (local Kawasaki dynamics)" in the write-up, and the
  multi-swap control "global Kawasaki dynamics." Judges familiar with the field will
  recognize them.
- Add greedy descent with restarts and simulated annealing as the "is MCMC even needed?"
  controls (Chang 2000; Shirai 2026, section 2).
- Count local optima under the swap move for every window; the landscape decides how much
  room any proposal has to help.

---

## 2. Quantum-enhanced MCMC

**Layden et al. (2023), *Nature* [full].** The original algorithm. Prepare the current bit
string, evolve it under a weighted mix of the problem Hamiltonian and a mixer, and measure
once to get the proposal:

$$
H = (1-\gamma)\,\alpha\, H_{\text{prob}} + \gamma\, H_{\text{mix}},
\qquad
\alpha = \frac{\lVert H_{\text{mix}} \rVert_F}{\lVert H_{\text{prob}} \rVert_F}
$$

The factor α puts both terms on the same scale. Because H is real and symmetric, proposing
x′ from x is exactly as likely as proposing x from x′. That symmetry lets the plain
Metropolis rule accept without correction, so the chain samples the intended Boltzmann
distribution. Layden et al. draw γ and the evolution time at random each step instead of
tuning them. On fully connected spin-glass instances with up to 10 spins, the quantum
proposal's spectral gap shrinks much more slowly with size than local or uniform classical
proposals (scaling exponent about 0.26 against 0.94–0.95). Their hardware run used a
second-order, palindromic Trotter circuit, and noise slowed convergence without breaking
correctness.

**Marshall et al. (2026) [full].** Applies QeMCMC to optimization: Maximum Independent Set
up to 117 qubits on IBM Heron devices, recovering the global optimum in all five instances.
It drops symmetry on purpose (first-order Trotter, warm-started states, 10,000 shots per step
filtered to the lowest-energy samples, five-replica parallel tempering) and calls the result
"purely a heuristic one." Two points carry over to our project. First, the baseline is
classical multi-bit-flip MCMC and the metric is median iterations to the known optimum, the
same framing as our scope. Second, on hardware, one shot per step was nearly as slow as
10,000 once overhead was counted, which argues against adaptive hardware chains.

**Critiques and refinements.**

- **Orfi & Sels (2024, PRA) [abs]:** no speedup over classical sampling on worst-case
  unstructured problems, and an upper bound that "rules out a speedup for any unital quantum
  proposal." At our sizes, proposal efficiency is the only defensible claim.
- **Hsieh, Orfi & Sels (2026, PRA) [abs]:** the central trade-off. The dynamics must spread
  far enough to propose non-local moves, but "excessive delocalization produces
  configurations unlikely to be accepted." This predicts an optimal evolution time — a curve
  we can measure.
- **Nakano et al. (2024, PRR) [abs]:** QAOA-style proposal circuits that stay symmetric for
  any parameters. The measurable acceptance rate tracks the spectral gap, so it can be used
  to tune parameters.
- **Shirai (2026) [abs, preprint]:** quantum dynamics as a transition kernel for
  optimization. Performance depends on "the interplay between Hamming-space nonlocality and
  energy-space locality," and "incorporating greedy descent substantially improves the
  performance." Both a design hint (pair proposals with greedy polishing) and a reason to
  include greedy as a control.
- **Ferguson & Wallden (2025, PRR) [abs]:** coarse-grained QeMCMC using fewer qubits than
  variables, a possible route past the qubit limit.

### Implication for our build

- The score-informed XY circuit is a count-preserving version of Layden's proposal. Credit
  Layden for the mechanism and Marshall for the optimization framing.
- Build each circuit as mix, score phase, mix with the second mixing block's gate order
  reversed. The whole circuit is then its own transpose, proposals are symmetric, and the
  Metropolis rule is valid (details in [`scope-review.md`](scope-review.md)).
- Sweep the evolution time or mixing angle and plot success against it, testing Hsieh et
  al.'s trade-off on real data.
- Log acceptance rate and the number of assets changed per accepted move.

---

## 3. Count-preserving quantum circuits

**XY mixers.** Hadfield et al. (2019) [meta] generalize QAOA to mixers that keep every
state feasible. Wang et al. (2020) [abs] show XY mixers, which move a 1 between qubits
without changing the total, give "a significant improvement over the general X mixer,"
and give ring and complete-graph implementations for different hardware layouts.

**Portfolios with XY mixers.** He et al. (2023, *npj QI*) [abs] study constrained
portfolio optimization with XY-mixer QAOA and run it on a 32-qubit trapped-ion processor.
They find performance is best when the starting state matches the mixer. Mancilla et al.
(2026) [abs, preprint] use a Dicke start and XY mixer for cardinality-constrained portfolios.
Their backtest is a single year of 10 stocks, so treat it as an example of the setup.
Brandhofer et al. (2022) [abs] cover the count-constrained portfolio QUBO and the effect of
shot and gate noise on QAOA.

**Why count preservation matters.** Lozano (2026) [abs, preprint] shows that the standard
count-penalty encoding was the binding constraint on D-Wave hardware, giving zero feasible
raw samples at every tested scale. Keeping the count in the circuit sidesteps this, at the
cost of wrong-count outcomes from hardware noise only.

**Count-preserving QeMCMC already exists.** Kawamata, Nakano & Fujii (2026, *Phys. Rev.
Applied*) [abs] use XY-mixer QAOA samples to build proposals "while preserving the
constraint" for fixed-count Ising problems. They report autocorrelation decay faster than
local and global Kawasaki dynamics by factors of about 14 and 7.7. Kawamata & Fujii (2026)
[abs, preprint] demonstrate the approach on an IBM Heron r2 processor with up to 1,064
variables, using trained neural-network surrogates rather than direct per-step sampling.
These are the closest prior work to our project and should be cited as such. Our
contribution is different: a direct circuit proposal per step, on real financial data, with
an exact answer key.

### Implication for our build

- Start each circuit from the current portfolio, which is a computational basis state;
  no Dicke-state preparation is needed.
- On hardware, prefer a ring XY mixer laid out on a 12-qubit ring of the device, and a
  score phase with single-qubit terms only, or nearest-neighbor pairs.
- Report the wrong-count rate as a direct measure of hardware noise.

---

## 4. Fair comparison

Hellstern, Schacht & Zaefferer (2026) [abs] show how much the comparison design matters.
On 180 benchmark QUBOs, branch-and-cut certified 176 optima within 600 s; with optima moved
to random bit strings, parallel tempering found every optimum in every run while
branch-and-cut found 4 of 10; linear-ramp QAOA gave no quality improvement over classical
methods. Their main lesson is to keep solution quality, proof of optimality and computational
cost as separate measures. Abbas et al. (2024, *Nat. Rev. Phys.*) [meta] set out benchmarking
good practice for quantum optimization.

### Implication for our build

- Report attempts, score evaluations, shots and runtime as separate columns, never one
  combined "speed" number.
- Use the exact answer key for gap and success rate. For 10 of 50, a mixed-integer quadratic
  solver can certify the optimum; a large count of portfolios does not by itself make the
  problem hard.

---

## 5. Financial inputs

Mean–variance selection comes from Markowitz (1952) [meta]. Estimated expected returns are
the dominant source of error (Chopra & Ziemba 1993 [meta]; Merton 1980 [meta]), and
covariance shrinkage helps (Ledoit & Wolf 2004 [meta]). Egger et al. (2020) [abs] and
Herman et al. (2023) [meta] survey quantum computing for finance and place portfolio
selection among the candidate applications.

### Implication for our build

The claim is about search on a fixed objective, not investment performance, so estimation
noise is acceptable. Say so explicitly. Use λ and the choice of windows to control
landscape difficulty, and report both.

---

## 6. What the literature does *not* support claiming

- A quantum speedup at any simulated size (Orfi & Sels 2024; Hellstern et al. 2026).
- That better proposals give better portfolios out of sample. The project measures search
  efficiency only.
- That Marshall's or Kawamata's results transfer directly. Their problems, proposal
  schemes and metrics differ from ours.
- That asset visit counts are probabilities, unless proposals are symmetric and the chains
  have demonstrably mixed.
