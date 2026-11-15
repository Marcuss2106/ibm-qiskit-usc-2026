# Narration (about 5:00)

One section per scene in `slides.py`. Speak it loosely; the slide timings leave room.
Numbers come from `data.json` and `../research_results.md`.

## 1. Title (0:00–0:25) — `Slide1Title`

"Most searches through portfolios take one small step at a time. We wanted to know
whether a small quantum circuit could suggest better steps, bigger jumps that still
head somewhere good. And we kept every problem small enough that we could check every
possible answer, so we always knew whether the search actually got it right."

## 2. How the search works (0:25–1:10) — `Slide2Search`

"Here's the search. You start with a portfolio, say four ETFs out of eight. You suggest a
change. If it's better you keep it, and every so often you keep it even when it's worse,
so you don't get stuck on the first decent answer. The usual change is simple: swap one
holding for another. Our version hands that choice to a quantum circuit. It tries lots
of trades at once, weighs each one by how good it would be, and gives you back one
suggestion. It never changes how many things you hold, and nothing else about the search
changes, so if the results differ, it's because of the move."

## 3. One big hill (1:10–1:50) — `Slide3Hill`

"First thing we found: most portfolio problems are boring in a very specific way. On real
ETF data, every quarter we looked at had exactly one best answer, and you could walk
straight uphill to it from anywhere. When we shuffled the correlations at random, the
landscape suddenly had about a dozen peaks. The reason is the market. Real assets mostly
move together, so there's never a second good answer competing with the first. So we went
looking for a problem where the market works against you."

## 4. Max-cut (1:50–2:30) — `Slide4MaxCut`

"That led us to max-cut. You draw a line through a graph, and every edge the line crosses
scores its weight. This first line scores eight. Move the line and you get fifteen. Now
look at a triangle: three nodes, all connected. However you draw the line, one edge stays
uncut. That little bit of tension, everywhere in a graph, is what gives you lots of good
answers that look nothing like each other."

## 5. The long–short book (2:30–3:20) — `Slide5Book`

"And here's the nice part: a market-neutral long–short book is exactly this problem. Each
ETF is a node. The weight on each edge is how closely two ETFs move together. Going long
or short is just which side of the line you're on. When you cut a heavy edge, you're
putting two look-alike assets on opposite sides, and that's precisely what makes the book
safer. Here's the real best book for the last quarter of 2025. And because SPY, IWM and EFA
all move together, one of those pairs always lands on the same side. On real data that
gives a genuinely bumpy landscape: about thirteen good-but-different books in a typical
quarter, and a greedy search picks the wrong one about four times out of five."

## 6. What the quantum move does (3:20–4:05) — `Slide6Quantum`

"So we ran the quantum move on it. With a circuit that lets any pair of assets trade, it
explored the good books faster than our best-tuned classical move, in 81 to 91 percent of
the quarters we held back for testing. Here's how we know it's the quantum part doing the
work: switch off the piece of the circuit that knows the scores, and the advantage goes
away. We also ran the circuit for real on IBM's Marrakesh processor: 35 starting books,
a thousand shots each, about twelve seconds of QPU time."

## 7. What we learned (4:05–4:40) — `Slide7Learned`

"Putting it together. We looked at four kinds of problem, and only one of them had room
for a smarter move: the long–short book. On that one, the quantum move was the fastest
explorer we tested. Two honest caveats: if all you want is the single best book, plain
swaps still get there first, and on today's hardware the noise cancels out the gain."

## 8. Where this leaves us (4:40–5:00) — `Slide8Close`

"So the takeaway is about where to look. Quantum moves pay off on tangled problems, the
ones with lots of good answers pulling in different directions, and market-neutral books
are a real example. As hardware gets quieter, those are the problems worth running on it.
Thanks."

## Backup (Q&A only) — `Backup`

Steps to reach the best book (ETFs, 8 vs 8, median): single swap 1,093, quantum 1,264,
parallel tempering 1,405, multi-swap 2,175. Hardware (Marrakesh, 35 books): 43% usable
shots; mixing speed 0.043 on hardware vs 0.090 ideal vs 0.061 for one swap; 12 QPU-seconds.
