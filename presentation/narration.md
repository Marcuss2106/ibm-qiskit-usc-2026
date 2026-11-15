# Narration (about 5:00, ~680 words)

Each section matches one scene in `slides.py`. Numbers come from `data.json` and
`../research_results.md`.

## 1. Title and question (0:00–0:30) — `Slide1Title`

"Quantum computers are often pitched for portfolio optimisation. We tested one concrete
idea: inside a standard search algorithm, can a quantum circuit propose smarter moves than
a classical one? And we kept problem sizes small enough to know the true answer, so every
number you'll see is measured, not estimated."

## 2. How the search works (0:30–1:20) — `Slide2Search`

"The search is called MCMC: propose a change, keep it if it's better, sometimes keep it
even if it's worse so you don't get stuck. Classically, a move swaps one asset for
another. Our quantum move runs a small circuit: it spreads the current portfolio over
many possible trades at once, tags each with its score, and recombines them so good
options reinforce each other. It always keeps the same number of holdings. Everything
else in the search stays identical, so we compare only the proposal."

## 3. The surprise (1:20–2:20) — `Slide3Surprise`

"First surprise. We built the classic problem, choosing 5 of 16 ETFs to balance return
and risk, across 64 quarters of real data. Every single quarter had exactly one peak. A
simple uphill search finds the best portfolio from any start, and the quantum proposal
was slower. The reason is the market: almost everything moves together, so there are
never competing good answers. When we replaced real correlations with random ones, we got
twelve peaks. So the data, not the algorithm, made it easy. And we saw the same thing
with stocks, factor models, and hedge books."

## 4. Max-cut and frustration (2:20–3:00) — `Slide4MaxCut`

"Hard search problems look like this: max-cut. Colour the dots so that connected dots
differ. Now look at a triangle. Whatever you do, one edge loses. That's called
frustration. Pile up enough triangles and you get many competing near-best answers:
exactly the rugged landscape where smarter proposals could matter."

## 5. The morph (3:00–3:50) — `Slide5Morph`

"Here's the twist. A market-neutral long–short book (half the assets long, half short,
chosen to minimise risk) is exactly a balanced max-cut. Assets are nodes, correlations
are edges, long and short are the two colours. Correlated assets want opposite sides, and
when three of them all move together, that's a frustrated triangle. So the same market
factor that made the first problem easy now makes this one hard: on real ETF data, a
median of 13 competing optima, and a greedy search fails about 80% of the time."

## 6. Results (3:50–4:35) — `Slide6Results`

"On this problem, with a circuit that lets any pair of assets trade, the quantum proposal
explores good portfolios faster than tuned classical long jumps, in 81 to 91 percent of
quarters we held out from tuning. Switch off the score information in the circuit and the
advantage disappears, so it really comes from the quantum part. But be precise about the
limits. Exploring isn't finding: for the single best portfolio, plain classical swaps
still get there first. And the winning circuit needs about 540 two-qubit gates. We ran a
cheaper version on IBM's Marrakesh processor: it works and stays nearly unbiased, but
noise cuts its speed in half."

## 7. Takeaways (4:35–5:00) — `Slide7Takeaways`

"So: quantum proposals won't speed up everyday portfolio optimisation; real markets are
too smooth. But on frustrated, max-cut-like problems such as market-neutral books, they
explore the space of good answers faster in simulation. That's useful for finding robust
positions and real alternatives, not for finding one answer faster. We didn't find a
speedup. We found where one could live, and measured how far today's hardware is from
reaching it. Thank you."

## Backup (Q&A only) — `Backup`

Race to the best book (ETFs, 8 long / 8 short, median attempts): single swap 1,093,
quantum 1,264, parallel tempering 1,405, multi-swap 2,175. Hardware (Marrakesh, 35
books): 43% usable shots; mixing gap 0.043 vs ideal 0.090 vs single swap 0.061;
12 QPU-seconds.
