# Narration (about 5:00; the slide 8 second build uses up the slack)

Bose's Fan Club: Marcus Sostak, Aigar Boltyenkov, Jesus Garcia.

One section per slide in `slides.py` (`FullTalkSlides`). Speak loosely, except the three
lines marked **word for word**. Numbers come from `data.json` and `../research_results.md`.

## 1. Title (0:00–0:25) — `slide1`

**Word for word:** "In five minutes you'll know where a quantum move actually beats
classical moves on a real finance problem, and where it doesn't."

(Click: the landscape appears.) "Searching for a good portfolio is a walk across a landscape
like this. Small steps get stuck on the first hill they climb. A quantum move can jump,
steered by the score. And every problem here is small enough that we checked every
possible answer, so we always know the truth."

## 2. The search loop (0:25–0:50) — `slide2`

"Our method is one loop. From the current book, propose a new one. Then a classical rule
decides: better books are always kept, worse ones sometimes, so the walk doesn't get
stuck. That's the formula at the bottom. (Click.) The usual proposal swaps one holding. We
put a quantum circuit in that one box and change nothing else, so any difference in
results comes from the move."

## 3. One peak vs many (0:50–1:30) — `slide3`

"First surprise: the textbook problem is too easy. Picking 5 of 16 ETFs has exactly one
peak in every quarter we checked, so plain swaps walk straight to it. (Click.) Now the
same ETFs as a long–short book, 8 long and 8 short: 13 peaks in this quarter. (Click.) We
tested four real problems; only the long–short book had room for a smarter move."

## 4. Max-cut (1:30–2:00) — `slide4`

"Why is long–short rugged? It's max-cut. Split the nodes into two groups; every edge the
line crosses scores its weight. This line scores 8, a better one scores 15. In a triangle,
even the best line leaves one edge uncut. Lots of triangles means lots of good answers
that look nothing alike."

## 5. The long–short book (2:00–2:40) — `slide5`

"A long–short book is exactly this. Each ETF is a node; edge weights are real correlations;
long or short is which side of the line you're on. Cutting a heavy edge puts two
look-alikes on opposite sides, which lowers risk. The objective is just the book's
variance: s transpose Sigma s, with each s plus or minus one and half on each side.
(Click.) Here's the real best book for
the last quarter of 2025, on 8 ETFs. SPY, IWM and EFA all move together, so one pair
always shares a side. At the full 16 ETFs that tension gives about 13 competing books per
quarter, and greedy picks the wrong one 4 times in 5."

## 6. Our move (2:40–3:20) — `slide6`

"Here's the circuit, one qubit per ETF: a mixer M of beta, made of XX plus YY gates that
trade a long for a short; a score phase that stamps each book with e to the minus i gamma
E; then the mixer in reverse. Measure, and you get the proposal: Q is the probability of
going from s to s-prime. Because the circuit is a palindrome, Q is symmetric, so the plain
Metropolis rule stays exact. (Click.) Left: one swap only reaches next-door books, all
equally likely. Right: the quantum move reaches far-off books, weighted by their scores.
This table is simulated, on the same instance we ran on hardware."

## 7. Main result (3:20–4:10) — `slide7`

**Word for word:** "On held-out quarters, the quantum move explores faster than tuned,
score-blind classical moves in 81 to 91 percent of them."

"Speed here is the spectral gap of each chain's exact transition matrix, relative to one
swap, and each method got one setting, tuned on even quarters and tested on odd ones. The
quantum move is about 2.7 times faster than one swap, ahead of the best-tuned multi-swap
at 2.2.
(Click.) The control: same circuit, score phase off, and it drops to 1.8, below the tuned
classical move. So the gain comes from the score phase. (Click.) Each square is one
held-out quarter: green, quantum wins. 81 percent on ETFs, 91 percent on stocks."

## 8. Limits and why a quantum move (4:10–4:50) — `slide8`

"Three honest limits. It's a sampling win: it explores good books faster. It's not a
faster optimizer: to hit the single best book, plain swaps get there first. And it's not
for today's hardware: the winning circuit needs about 540 two-qubit gates, and the cheap
version we ran on ibm_marrakesh mixed slower than one swap."

(Click.) "So why a quantum move at all? Classical moves either steer by the score or jump
far. A locally balanced swap steers by the score, checking 30 neighbours every step, and
at our size it's faster still. But to steer *and* jump far classically, you'd have to score
every book several swaps away, and that explodes as books grow. The quantum move does both
with one circuit run. At 462 books, local classical still wins; whether that flips at
scale is the open question."

## 9. Contributions (4:50–5:10) — `slide9`

"We found where real portfolio landscapes get rugged, built a quantum move that explores
them faster than tuned, score-blind classical moves, and traced the gain to the score
phase." **Word for word:** "Rugged problems, quantum moves." Leave this slide up for Q&A.

## Backup (Q&A only) — `backup`

- Speeds vs one swap (ETFs, 6 vs 6): several swaps tuned 2.22, quantum 2.67, quantum with
  phase off 1.84, locally balanced 3.42 (30 score checks per step).
- Steps to the best book (ETFs, 8 vs 8, median): single swap 1,093, quantum 1,264, parallel
  tempering 1,405, multi-swap 2,175.
- Hardware (ibm_marrakesh, 4 vs 4, 35 books): 43% usable shots; mixing 0.043 on hardware vs
  0.090 ideal vs 0.061 for one swap; 12 QPU-seconds.
