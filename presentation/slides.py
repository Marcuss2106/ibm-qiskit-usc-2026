"""Five-minute talk: rugged problems, quantum moves.

Follows a 3Blue1Brown-style outline (assertion headlines, speaker notes,
limits slide, contributions ending), plus the max-cut slides.

Render (from presentation/, after `python make_data.py` has written data.json):
    manim -pql slides.py FullTalk                       # quick preview, timed video
    manim -qh  slides.py FullTalk                       # 1080p video
    manim-slides render --quality h slides.py FullTalkSlides && manim-slides present FullTalkSlides
Every beat() is a timed pause in the video and a click (with speaker notes) in the slideshow.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UP, UR,
    ArcBetweenPoints, BackgroundRectangle, Circle, Create, DashedLine, Dot,
    Arrow, CurvedArrow, FadeIn, FadeOut, Flash, FunctionGraph, GrowFromEdge, ImageMobject, Indicate, LaggedStart, MathTex,
    Line, ManimColor, MoveAlongPath, Rectangle, RoundedRectangle, Square, Surface, Table, Text,
    ThreeDAxes, ThreeDScene, Transform, ValueTracker, VGroup, Write, always_redraw, config,
)
from manim.constants import RESAMPLING_ALGORITHMS

try:  # optional: clickable slideshow via manim-slides
    from manim_slides import Slide, ThreeDSlide
except ImportError:  # video rendering still works without it
    Slide = ThreeDSlide = None

DATA = json.loads((Path(__file__).with_name("data.json")).read_text())
NUM = DATA["numbers"]
SLOGAN = "Rugged problems, quantum moves."
TEAM = "Bose's Fan Club"
MEMBERS = "Marcus Sostak, Aigar Boltyenkov, Jesus Garcia"

# Speaker notes, one entry per click, in deck order. Markdown bullets; shown in the presenter view (press S).
NOTES = {
    "title": """
- **Say word for word:** "In five minutes you'll know where a quantum move actually beats classical moves on a real finance problem, and where it doesn't."
- We're Bose's Fan Club: Marcus, Aigar and Jesus.
- The method is QeMCMC, quantum-enhanced Markov chain Monte Carlo: a classical MCMC search where a quantum circuit proposes each move.
""",
    "promise": """
- Searching for a portfolio is a walk over a landscape of scores.
- Classical MCMC takes small steps and gets stuck on the first hill.
- QeMCMC can jump, and the jump is steered by the score.
- Every problem is small enough that we checked every possible answer, so each claim is measured against the truth.
""",
    "loop": """
- Our method is one loop: from the current book, propose a new one, then accept or reject it.
- The acceptance rule is classical Metropolis: better books are always kept, worse ones sometimes (set by temperature T), so the walk doesn't get stuck.
- E is the book's risk score; lower is better.
""",
    "quantum_box": """
- The usual proposal swaps one holding (watch EEM and IEF trade places).
- We replace only that box with a quantum circuit, then measure it to get the proposed book.
- The acceptance rule stays classical, so any difference in results comes from the move.
""",
    "long_only": """
- First surprise: the textbook problem is too easy.
- Long-only, pick 5 of 16 ETFs: exactly one peak, in all 64 quarters we checked.
- Plain swaps walk straight up from any start; no smarter move can help.
""",
    "long_short": """
- Same ETFs, same quarter, now as a long–short book, 8 long and 8 short: 13 peaks.
- Each peak is a real local optimum; width shows how many starting books climb to it.
- Rugged landscapes like this are where a smarter move can matter.
""",
    "four_problems": """
- We tested four real problems.
- Long-only, factor selection and a 16-instrument hedge book were all single-peaked.
- Only the long–short book was rugged: about 13 good but different books per quarter.
""",
    "maxcut": """
- Why is long–short rugged? It's max-cut.
- Split the nodes into two groups; every edge the line crosses scores its weight.
- This line scores 8; a better line scores 15.
""",
    "triangle": """
- In a triangle, even the best line leaves one edge uncut. That's frustration.
- Pile up triangles and you get many good answers that look nothing alike.
""",
    "graph": """
- A long–short book is exactly this. Each ETF is a node; edge weights are real correlations.
- Long or short is which side of the line you're on.
- The objective is the book's variance, s-transpose Sigma s over n squared, with each s = ±1 and half on each side.
- Cutting a heavy edge puts two look-alikes on opposite sides, which lowers risk.
""",
    "best_book": """
- This is the real best book for Q4 2025 on 8 ETFs (4 vs 4).
- SPY, IWM and EFA all move together, so one pair always shares a side.
- At 16 ETFs that tension gives about 13 competing books per quarter, and greedy picks the wrong one 4 times in 5.
""",
    "circuit": """
- The circuit: one qubit per ETF (SPY is fixed long, since flipping every side gives the same risk).
- Mixer M(β): XX+YY gates that trade a long for a short, so the book stays balanced.
- Score phase P(γ) = e^(−iγE): stamps each book with its score. This is where the score steers the jump.
- Then the mixer in reverse, and measure. Q is the probability of proposing s′ from s.
- The circuit is a palindrome, so Q is symmetric and plain Metropolis stays exact.
""",
    "heatmaps": """
- Each row: where a move can go from one book.
- One swap only reaches next-door books, all equally likely.
- The quantum move also reaches far-off books, weighted by their scores.
- Simulated, on the same 35-book instance we ran on hardware.
""",
    "bars": """
- **Say word for word:** "On held-out quarters, the quantum move explores faster than tuned, score-blind classical moves in 81 to 91 percent of them."
- Speed is the spectral gap of each chain's exact transition matrix, relative to one swap.
- Fair test: one setting per method, tuned on even quarters, tested on odd ones.
- Quantum is about 2.7× one swap, ahead of tuned multi-swap at 2.2.
""",
    "phase_off": """
- The control: same circuit with the score phase switched off.
- It drops to 1.84, below tuned multi-swap.
- So the gain comes from the score information in the circuit, not from jumping farther.
""",
    "grid": """
- Each square is one held-out quarter, 2010 to 2025.
- Green: quantum explored faster than the tuned classical move. Brighter: bigger gap.
- 81% of ETF quarters, 91% of stock quarters.
""",
    "limits": """
- Three honest limits.
- It's a sampling win: it explores the good books faster.
- Not a faster optimizer: to hit the single best book, plain swaps get there first (1,093 vs 1,264 steps).
- Not for today's hardware: the winning circuit needs about 540 two-qubit gates; our cheap version on ibm_marrakesh mixed slower than one swap.
""",
    "why_quantum": """
- So why a quantum move at all?
- Classical moves either steer by the score or jump far.
- The locally balanced swap steers by score, checks 30 neighbours per step, and is faster still at our size (3.42).
- Steering and jumping far classically means scoring every book several swaps away, which explodes as books grow.
- The quantum move does both with one circuit run. Whether that wins at scale is the open question.
""",
    "contributions": """
- We found where real portfolio landscapes get rugged: market-neutral long–short books.
- We built a QeMCMC move that explores them faster than tuned, score-blind classical moves.
- We traced the gain to the score phase, and ran the circuit on IBM hardware.
- **Say word for word:** "Rugged problems, quantum moves."
- Leave this slide up for Q&A.
""",
    "backup": """
- Q&A only: speed table, race to the best book, hardware details.
""",
}

BG = ManimColor("#0f1117")
FG = ManimColor("#e8ecf2")
MUTED = ManimColor("#8b94a5")
LONG = ManimColor("#4c9be8")
SHORT = ManimColor("#f2994a")
QUANTUM = ManimColor("#b57bff")
CLASSICAL = ManimColor("#9aa4b2")
GOOD = ManimColor("#6fcf97")
BAD = ManimColor("#eb5757")
WARM = ManimColor("#e2574c")
COOL = ManimColor("#2bb3a3")
CUT = ManimColor("#f2c94c")

config.background_color = BG


# ---------------------------------------------------------------- helpers
def T(s, size=32, color=FG, weight="NORMAL"):
    return Text(s, font_size=size, color=color, weight=weight)


def fit(m, max_width=13.0):
    """Shrink a mobject to fit the frame width (frame is ~14.2 units wide)."""
    if m.width > max_width:
        m.scale_to_fit_width(max_width)
    return m


def heading(s):
    """Assertion headline: the slide's claim as a sentence."""
    return fit(T(s, 36, FG, "BOLD"), 13.2).to_edge(UP, buff=0.4)


def hill(x):
    return 2.4 * np.exp(-(x / 2.6) ** 2) - 1.6


# illustrative rugged landscape: (centre, height, width) of each bump; the tallest is at x = 1.0
RUGGED_PEAKS = ((-3.8, 1.1, 0.7), (-1.4, 0.7, 0.5), (1.0, 2.3, 0.8), (4.0, 1.4, 0.6))


def rugged(x):
    return -1.6 + sum(h * np.exp(-((x - c) / w) ** 2) for c, h, w in RUGGED_PEAKS)


def landscape(f, x0=-6, x1=6, color=FG, width=4):
    return FunctionGraph(f, x_range=[x0, x1, 0.02], color=color, stroke_width=width)


def walker(f, tracker, color, shift=ORIGIN, radius=0.12):
    return always_redraw(
        lambda: Dot(np.array([tracker.get_value(), f(tracker.get_value()), 0]) + shift, radius=radius, color=color)
    )


def bar(value, max_value, height, width, color, label, value_label, x, base_y):
    """Bar whose bottom edge sits at (x, base_y), with label below and value above."""
    rect = Rectangle(width=width, height=height * value / max_value, fill_color=color, fill_opacity=0.9,
                     stroke_width=0).move_to(np.array([x, base_y, 0]), aligned_edge=DOWN)
    lab = T(label, 20, MUTED).next_to(rect, DOWN, buff=0.15)
    val = T(value_label, 26, FG, "BOLD").next_to(rect, UP, buff=0.1)
    return VGroup(rect, lab, val)


def M(tex, size=34, color=FG):
    """LaTeX formula in the deck's colours."""
    return MathTex(tex, font_size=size, color=color)


def weight_label(value, at, size=18, color=FG):
    lab = T(value, size, color, "BOLD").move_to(at)
    return VGroup(BackgroundRectangle(lab, color=BG, fill_opacity=0.9, buff=0.05), lab)


def side_of(points, centre, normal):
    return [1 if np.dot(p - centre, normal) > 0 else -1 for p in points]


def table(rows, header, size=22, highlight=None, hcolor=QUANTUM):
    t = Table(rows, col_labels=[T(h, size, FG, "BOLD") for h in header],
              element_to_mobject=lambda s: T(s, size, FG),
              include_outer_lines=False, line_config={"stroke_color": MUTED, "stroke_width": 1},
              h_buff=0.55, v_buff=0.28)
    t.remove(*t.get_vertical_lines())  # horizontal rules only (vertical ones rendered as stray stubs)
    if highlight is not None:
        t.get_rows()[highlight].set_color(hcolor)
    return t


def heat_rgb(t):
    """0..1 -> background, then purple, then yellow (heat-map colours)."""
    stops = [np.array([15, 17, 23]), np.array([181, 123, 255]), np.array([242, 201, 76])]
    t = np.clip(t, 0, 1)
    lo = np.where(t < 0.5, 0, 1)
    f = np.where(t < 0.5, t / 0.5, (t - 0.5) / 0.5)
    a = np.array(stops)[lo]
    b = np.array(stops)[lo + 1]
    rgb = (a + (b - a) * f[..., None]).astype(np.uint8)
    alpha = np.full(rgb.shape[:2] + (1,), 255, dtype=np.uint8)
    return np.concatenate([rgb, alpha], axis=-1)  # RGBA uint8, as ImageMobject expects


def heatmap_image(matrix, height=3.0):
    """Heat map as a grid of coloured squares (works with the 3D camera, unlike ImageMobject)."""
    m = np.asarray(matrix, float)
    rgb = heat_rgb(np.sqrt(m / m.max()))[..., :3]
    n = len(m)
    s = height / n
    return VGroup(*[
        Square(s, stroke_width=0, fill_opacity=1,
               fill_color=ManimColor.from_rgb(tuple(int(c) for c in rgb[i, j]))).move_to(np.array([j * s, -i * s, 0]))
        for i in range(n) for j in range(n)
    ])


def peak_surface(axes, peaks, resolution=40):
    def f(u, v):
        z = 0.02
        for p in peaks:
            w = 0.11 + 0.36 * np.sqrt(p["share"])
            z = max(z, p["h"] * np.exp(-((u - p["x"]) ** 2 + (v - p["y"]) ** 2) / (2 * w * w)))
        return z

    s = Surface(lambda u, v: axes.c2p(u, v, f(u, v)), u_range=[-1.25, 1.25], v_range=[-1.25, 1.25],
                resolution=(resolution, resolution), stroke_width=0.3, stroke_color=BG, fill_opacity=0.95)
    s.set_fill_by_value(axes=axes, colorscale=[(COOL, 0.0), (QUANTUM, 0.45), (CUT, 0.85), (WARM, 1.0)], axis=2)
    return s


def clear(scene):
    for m in scene.mobjects:
        m.clear_updaters()
    scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=0.6)


# ---------------------------------------------------------------- slides
class Talk(ThreeDScene):
    def beat(self, seconds: float, notes: str = ""):
        """Hold point: timed wait in the video, click-to-advance (with notes) in the slideshow."""
        if Slide is not None and isinstance(self, Slide):
            self._base_slide_config.notes = notes.strip()  # notes for the slide ending here, not the next one
            self.next_slide()
        else:
            self.wait(seconds)

    # ---------------------------------------------- 1. title and promise (~0:20)
    def slide1(self):
        title = fit(T(SLOGAN, 54, FG, "BOLD"), 12.5)
        sub = VGroup(
            T("QeMCMC: quantum-enhanced Markov chain Monte Carlo", 30, QUANTUM, "BOLD"),
            T("A small quantum circuit proposes each move of a classical MCMC search through real ETF portfolios",
              24, MUTED),
        ).arrange(DOWN, buff=0.15)
        fit(sub, 12.5)
        team = VGroup(T(TEAM, 26, FG, "BOLD"), T(MEMBERS, 22, MUTED),
                      T("IBM Quantum x USC Hackathon 2026", 20, MUTED)).arrange(DOWN, buff=0.15)
        VGroup(title, sub, team).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=1.4)
        self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(team, shift=UP * 0.2))
        self.beat(3, notes=NOTES["title"])
        self.play(FadeOut(team), VGroup(title, sub).animate.scale(0.6).to_edge(UP, buff=0.3))

        shift = DOWN * 0.55
        curve = landscape(rugged, color=MUTED).shift(shift)
        self.play(Create(curve), run_time=1.0)
        tc = ValueTracker(-5.6)
        cdot = walker(rugged, tc, CLASSICAL, shift=shift)
        self.add(cdot)
        for x in (-5.1, -4.6, -4.2, -3.8):  # small uphill steps, then stuck on the first local peak
            self.play(tc.animate.set_value(x), run_time=0.35)
        stuck = T("stuck", 20, CLASSICAL).next_to(np.array([-3.8, rugged(-3.8), 0]) + shift, UP, buff=0.25)
        self.play(FadeIn(stuck), Indicate(cdot, color=CLASSICAL))
        qdot = Dot(np.array([5.2, rugged(5.2), 0]) + shift, radius=0.12, color=QUANTUM)
        path = ArcBetweenPoints(qdot.get_center(), np.array([1.0, rugged(1.0), 0]) + shift, angle=-PI / 2)
        self.play(FadeIn(qdot))
        self.play(MoveAlongPath(qdot, path), run_time=1.1)
        self.play(Flash(qdot, color=QUANTUM))
        legend = VGroup(
            VGroup(Dot(color=CLASSICAL), T("classical MCMC: one small step at a time", 22, CLASSICAL)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=QUANTUM), T("QeMCMC: jumps steered by the score", 22, QUANTUM)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR).shift(DOWN * 1.7)
        promise = T("Where does a quantum move actually beat classical moves?", 30, FG, "BOLD").to_edge(DOWN, buff=0.9)
        note = T("Every problem is small enough that we can check every possible answer.", 22, MUTED)\
            .next_to(promise, DOWN, buff=0.2)
        self.play(FadeIn(legend), Write(promise))
        self.play(FadeIn(note))
        self.beat(6, notes=NOTES["promise"])
        clear(self)

    # ---------------------------------------------- 2. the search is a walk (~0:25)
    def slide2(self):
        h = heading("The search is a loop: propose a new book, then accept or reject it")
        self.play(Write(h))
        tick = DATA["tickers"]

        def row(highlight, y=1.4):
            cells = VGroup()
            for i, t in enumerate(tick):
                on = i in highlight
                box = RoundedRectangle(corner_radius=0.08, width=1.05, height=0.62,
                                       stroke_color=LONG if on else MUTED, stroke_width=3,
                                       fill_color=LONG, fill_opacity=0.35 if on else 0.0)
                cells.add(VGroup(box, T(t, 20, FG if on else MUTED)))
            return cells.arrange(RIGHT, buff=0.12).move_to(UP * y)

        r = row({0, 1, 4, 6}, y=2.0)
        count = T("4 held", 24, LONG).next_to(r, RIGHT, buff=0.3)
        self.play(FadeIn(r), FadeIn(count))

        # the architecture: one loop, quantum proposal + classical decision
        def stage(x, title, sub, color):
            box = RoundedRectangle(corner_radius=0.12, width=3.5, height=1.25, stroke_color=color, stroke_width=3,
                                   fill_color=color, fill_opacity=0.12).move_to(np.array([x, 0.45, 0]))
            txt = fit(VGroup(T(title, 24, color, "BOLD"), T(sub, 18, MUTED)).arrange(DOWN, buff=0.1), 3.2).move_to(box)
            return VGroup(box, txt)

        cur = stage(-4.5, "Current book  s", "where the walk is now", FG)
        prop = stage(0.0, "Propose  s′", "usual: swap one holding", CLASSICAL)
        acc = stage(4.5, "Accept or reject", "classical Metropolis rule", GOOD)
        a1 = Arrow(cur.get_right(), prop.get_left(), buff=0.1, color=MUTED, stroke_width=4)
        a2 = Arrow(prop.get_right(), acc.get_left(), buff=0.1, color=MUTED, stroke_width=4)
        back = CurvedArrow(acc[0].get_bottom() + DOWN * 0.05, cur[0].get_bottom() + DOWN * 0.05, angle=-PI / 5,
                           color=MUTED, stroke_width=4)
        rep = T("repeat", 18, MUTED).next_to(back, DOWN, buff=0.08)
        self.play(LaggedStart(FadeIn(cur), Create(a1), FadeIn(prop), Create(a2), FadeIn(acc), lag_ratio=0.3),
                  run_time=2.0)
        self.play(Create(back), FadeIn(rep), run_time=0.8)
        rule = M(r"P_{\text{accept}}(s \to s') = \min\left(1,\ e^{-[E(s') - E(s)]/T}\right)", 34)\
            .move_to(np.array([0, -2.0, 0]))
        rule_note = T("E = the book's risk score (lower is better). Better books are always kept; worse ones "
                      "sometimes, so the walk doesn't get stuck.", 18, MUTED).next_to(rule, DOWN, buff=0.15)
        fit(rule_note, 12.5)
        self.play(Write(rule), FadeIn(rule_note), run_time=1.2)
        self.beat(4, notes=NOTES["loop"])

        self.play(Transform(r, row({0, 1, 3, 6}, y=2.0)), run_time=1.0)
        self.play(Indicate(r[3], color=LONG), Indicate(r[4], color=MUTED), run_time=0.8)
        ours = T("We swap in a quantum circuit for the proposal, and change nothing else.", 26, QUANTUM, "BOLD")\
            .to_edge(DOWN, buff=0.45)
        qprop = stage(0.0, "Propose  s′", "quantum circuit, then measure", QUANTUM)
        self.play(Transform(prop, qprop), FadeIn(ours), run_time=1.0)
        self.beat(10, notes=NOTES["quantum_box"])
        clear(self)

    # ---------------------------------------------- 3. one peak vs many: 3D landscape (~0:45)
    def slide3(self):
        h = heading("Long-only portfolios have one peak; long-short books have many")
        self.add_fixed_in_frame_mobjects(h)
        self.play(Write(h))
        L = DATA["landscape3d"]
        axes = ThreeDAxes(x_range=[-1.3, 1.3], y_range=[-1.3, 1.3], z_range=[0, 1.2],
                          x_length=7, y_length=7, z_length=3.2).shift(DOWN * 0.6)
        lo = peak_surface(axes, L["long_only"])
        ls = peak_surface(axes, L["long_short"])
        self.move_camera(phi=62 * DEGREES, theta=-55 * DEGREES, zoom=0.85, run_time=1.2)
        lab = T(f"Long-only\npick 5 of 16 ETFs\n{len(L['long_only'])} peak", 26, GOOD, "BOLD")\
            .to_edge(RIGHT, buff=0.4).shift(UP * 1.2)
        self.add_fixed_in_frame_mobjects(lab)
        self.play(Create(lo), FadeIn(lab), run_time=2.0)
        self.beat(4, notes=NOTES["long_only"])
        lab2 = T(f"Long-short\n16 ETFs, 8 vs 8\n{len(L['long_short'])} peaks", 26, CUT, "BOLD")\
            .to_edge(RIGHT, buff=0.4).shift(UP * 1.2)
        self.add_fixed_in_frame_mobjects(lab2)
        self.play(Transform(lo, ls), FadeOut(lab), FadeIn(lab2), run_time=2.5)
        key = fit(T("Each peak is a real local optimum. Height = its score.\n"
                    "Width = how many starting books climb to it. Same quarter, same ETFs.", 20, MUTED), 7.0)\
            .to_corner(DOWN + LEFT).shift(UP * 0.1 + RIGHT * 0.2)
        self.add_fixed_in_frame_mobjects(key)
        self.play(FadeIn(key))
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.beat(3, notes=NOTES["long_short"])
        self.play(FadeOut(lo), FadeOut(lab2), FadeOut(key), run_time=0.8)
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1.0, run_time=1.0)

        t_title = T("Four real problems we tested", 28, FG, "BOLD")
        t1 = table([
            ["Long-only: pick 5 of 16 ETFs", "1", "No"],
            ["Pick the factors that explain SPY", "1", "No"],
            ["Hedge book: 16 instruments, 5 risk factors", "1", "No"],
            ["Long-short: 16 ETFs, 8 vs 8", str(len(L["long_short"])), "Yes"],
        ], ["Problem", "Peaks in a typical quarter", "Room for a smarter move?"], 22, highlight=4)
        g = fit(VGroup(t_title, t1).arrange(DOWN, buff=0.35), 12.6).move_to(DOWN * 0.3)
        self.add_fixed_in_frame_mobjects(g)
        self.play(FadeIn(t_title), FadeIn(t1), run_time=1.2)
        self.beat(10, notes=NOTES["four_problems"])
        clear(self)

    # ---------------------------------------------- 4. max-cut with a cut line (~0:35)
    def slide4(self):
        h = heading("Max-cut: draw a line and score every heavy edge it crosses")
        rule = T("Two groups, one line. Each edge the line crosses scores its weight.", 24, MUTED)\
            .next_to(h, DOWN, buff=0.2)
        self.play(Write(h), FadeIn(rule))
        centre = LEFT * 3.4 + DOWN * 0.45
        pos = [centre + 1.6 * np.array([np.cos(a), np.sin(a), 0])
               for a in np.linspace(PI / 2, PI / 2 + 2 * PI, 6, endpoint=False)]
        # outer ring plus three chords that skip one node (no chord passes through the centre)
        edges = [(0, 1, 4), (1, 2, 2), (2, 3, 5), (3, 4, 3), (4, 5, 2), (5, 0, 4), (0, 2, 3), (2, 4, 4), (3, 5, 1)]
        lines = VGroup(*[Line(pos[a], pos[b], color=MUTED, stroke_width=3) for a, b, _ in edges])
        wlabs = VGroup(*[weight_label(str(w), (pos[a] + pos[b]) / 2, 18) for a, b, w in edges])
        nodes = VGroup(*[Dot(p, radius=0.2, color=MUTED) for p in pos])
        self.play(Create(lines), FadeIn(nodes), FadeIn(wlabs), run_time=1.3)

        def cut_for(normal_deg):
            nrm = np.array([np.cos(np.radians(normal_deg)), np.sin(np.radians(normal_deg)), 0])
            sides = side_of(pos, centre, nrm)
            direction = np.array([-nrm[1], nrm[0], 0])
            line = DashedLine(centre - 1.9 * direction, centre + 1.9 * direction, color=CUT, stroke_width=5)
            total = sum(w for a, b, w in edges if sides[a] != sides[b])
            return sides, line, total

        cuts = sorted((cut_for(d) for d in (75, 15)), key=lambda c: c[2])  # weaker cut first
        cut_line, score = None, None
        for sides, line, total in cuts:
            anims = [nd.animate.set_color(LONG if s > 0 else SHORT) for nd, s in zip(nodes, sides)]
            anims += [ln.animate.set_color(CUT if sides[a] != sides[b] else MUTED)
                      .set_stroke(width=6 if sides[a] != sides[b] else 2) for ln, (a, b, _) in zip(lines, edges)]
            new_score = T(f"cut weight: {total}", 26, CUT, "BOLD").move_to(centre + DOWN * 2.3)
            if cut_line is None:
                cut_line, score = line, new_score
                self.play(Create(cut_line), *anims, FadeIn(score), run_time=1.2)
            else:
                self.play(Transform(cut_line, line), *anims, Transform(score, new_score), run_time=1.2)
            self.wait(1.2)
        better = T("Better line, bigger score.", 22, GOOD).next_to(score, DOWN, buff=0.1)
        self.play(FadeIn(better))
        self.beat(2, notes=NOTES["maxcut"])

        # triangle: no line cuts all three edges
        tp = [RIGHT * 3.6 + UP * 0.55, RIGHT * 2.4 + DOWN * 1.3, RIGHT * 4.8 + DOWN * 1.3]
        tri_e = [(0, 1, 3), (1, 2, 4), (0, 2, 5)]
        tri_l = VGroup(*[Line(tp[a], tp[b], color=MUTED, stroke_width=4) for a, b, _ in tri_e])
        tri_w = VGroup(*[weight_label(str(w), (tp[a] + tp[b]) / 2, 18) for a, b, w in tri_e])
        tri_n = VGroup(*[Dot(p, radius=0.22, color=MUTED) for p in tp])
        tri_t = T("Three nodes, all connected:", 22, FG).next_to(tri_n, UP, buff=0.3)
        self.play(Create(tri_l), FadeIn(tri_n), FadeIn(tri_w), FadeIn(tri_t))
        tcentre = sum(tp) / 3
        tri_line = None
        for normal_deg in (100, 150):  # leaves the 4 uncut, then the best cut (only the 3 uncut)
            nrm = np.array([np.cos(np.radians(normal_deg)), np.sin(np.radians(normal_deg)), 0])
            sides = side_of(tp, tcentre, nrm)
            direction = np.array([-nrm[1], nrm[0], 0])
            new_line = DashedLine(tcentre - 1.45 * direction, tcentre + 1.45 * direction, color=CUT, stroke_width=5)
            anims = [nd.animate.set_color(LONG if s > 0 else SHORT) for nd, s in zip(tri_n, sides)]
            anims += [ln.animate.set_color(CUT if sides[a] != sides[b] else BAD) for ln, (a, b, _) in zip(tri_l, tri_e)]
            if tri_line is None:
                tri_line = new_line
                self.play(Create(tri_line), *anims, run_time=0.9)
            else:
                self.play(Transform(tri_line, new_line), *anims, run_time=0.9)
            uncut = [k for k, (a, b, _) in enumerate(tri_e) if sides[a] == sides[b]][0]
            self.play(Indicate(tri_l[uncut], color=BAD, scale_factor=1.12), run_time=0.7)
        frus = fit(T("Even the best line leaves one edge uncut.\nThat tension is what makes it hard.", 22, BAD), 5.6)\
            .move_to(np.array([3.6, -2.35, 0]))
        self.play(FadeIn(frus))
        foot = T("Lots of triangles means lots of good, very different answers.", 24, FG).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(foot))
        self.beat(12, notes=NOTES["triangle"])
        clear(self)

    # ---------------------------------------------- 5. the long-short book is a max-cut (~0:40)
    def slide5(self):
        h = heading("A long-short book is a max-cut on the correlation graph")
        self.play(Write(h))
        tick = DATA["tickers"]
        corr = np.array(DATA["corr"])
        best = DATA["best_signs"]
        n = len(tick)
        centre = LEFT * 3.8 + DOWN * 0.35
        start = [centre + 2.35 * np.array([np.cos(a), np.sin(a), 0])
                 for a in np.linspace(PI / 2, PI / 2 + 2 * PI, n, endpoint=False)]
        longs = [i for i in range(n) if best[i] > 0]
        shorts = [i for i in range(n) if best[i] < 0]
        target = list(start)
        for k, i in enumerate(longs):
            target[i] = np.array([-5.4, 1.2 - k * 1.05, 0])
        for k, i in enumerate(shorts):
            target[i] = np.array([-2.2, 1.2 - k * 1.05, 0])

        dots = VGroup(*[Dot(p, radius=0.33, color=MUTED) for p in start])
        names = VGroup(*[T(t, 17, BG, "BOLD").move_to(p) for t, p in zip(tick, start)])
        for nm, d in zip(names, dots):
            nm.add_updater(lambda m, d=d: m.move_to(d.get_center()))
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if abs(corr[i, j]) >= 0.25]
        lines = VGroup()
        for i, j in pairs:
            c = corr[i, j]
            ln = Line(start[i], start[j], color=WARM if c > 0 else COOL, stroke_width=1 + 6 * abs(c),
                      stroke_opacity=0.35 + 0.5 * abs(c))
            ln.add_updater(lambda m, i=i, j=j: m.put_start_and_end_on(dots[i].get_center(), dots[j].get_center()))
            lines.add(ln)
        wl = VGroup()
        placed = []
        for i, j in pairs:
            if abs(corr[i, j]) < 0.78:  # label only the strongest pairs; more would crowd the left cluster
                continue
            # slide the label along its edge until it is clear of every other node
            others = [start[k] for k in range(n) if k not in (i, j)]

            def clear_at(f):
                q = start[i] + f * (start[j] - start[i])
                return (min(np.linalg.norm(q - o) for o in others) > 0.75
                        and all(np.linalg.norm(q - r) > 0.6 for r in placed))

            frac = next((f for f in (0.5, 0.4, 0.6, 0.3, 0.7, 0.25, 0.75) if clear_at(f)), 0.5)
            placed.append(start[i] + frac * (start[j] - start[i]))
            lab = weight_label(f"{corr[i, j]:.2f}", start[i] + frac * (start[j] - start[i]), 15)
            lab.add_updater(lambda m, i=i, j=j, f=frac: m.move_to(dots[i].get_center()
                                                                  + f * (dots[j].get_center() - dots[i].get_center())))
            wl.add(lab)
        self.add(lines, dots, names)
        self.play(*[Create(ln) for ln in lines], FadeIn(dots), FadeIn(names), run_time=1.4)
        self.play(FadeIn(wl))

        expl = VGroup(
            T("Node = an ETF", 24, FG),
            T("Edge weight = how closely two ETFs move together", 24, WARM),
            T("(teal edge = they tend to move opposite)", 20, COOL),
            T("Side of the line = long or short", 24, LONG),
            T("Cut a heavy edge = split two look-alikes = lower risk", 24, CUT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit(expl, 6.2).move_to(RIGHT * 3.3 + UP * 1.5)
        for e in expl:
            self.play(FadeIn(e, shift=LEFT * 0.2), run_time=0.5)
        obj = VGroup(
            M(r"\min_s\ E(s) = \frac{s^{\top}\Sigma\, s}{n^2}", 36),
            M(r"s_i \in \{+1, -1\}, \qquad \sum_{i} s_i = 0", 28, MUTED),
        ).arrange(DOWN, buff=0.15).next_to(expl, DOWN, buff=0.35)
        obj_note = T("the book's risk: half long, half short, equal size", 18, MUTED).next_to(obj, DOWN, buff=0.1)
        self.play(Write(obj), FadeIn(obj_note), run_time=1.0)
        self.beat(4, notes=NOTES["graph"])

        cut = DashedLine(np.array([-3.8, 1.85, 0]), np.array([-3.8, -2.65, 0]), color=CUT, stroke_width=6)
        lab_l = T("long", 22, LONG, "BOLD").move_to(np.array([-5.4, 1.95, 0]))
        lab_s = T("short", 22, SHORT, "BOLD").move_to(np.array([-2.2, 1.95, 0]))
        self.play(FadeOut(wl), run_time=0.4)
        self.play(*[d.animate.move_to(p).set_color(LONG if best[i] > 0 else SHORT)
                    for i, (d, p) in enumerate(zip(dots, target))], run_time=2.0)
        self.play(Create(cut), FadeIn(lab_l), FadeIn(lab_s))
        crossing = [k for k, (i, j) in enumerate(pairs) if best[i] != best[j] and corr[i, j] > 0]
        self.play(*[lines[k].animate.set_color(CUT).set_stroke(opacity=0.95) for k in crossing], run_time=0.8)
        tri = [tick.index(t) for t in ("SPY", "IWM", "EFA")]
        ring = VGroup(*[Circle(radius=0.45, color=CUT, stroke_width=4).move_to(dots[i]) for i in tri])
        note = fit(T("SPY, IWM and EFA all move together:\none pair always shares a side.", 22, CUT), 6.4)\
            .next_to(obj_note, DOWN, buff=0.3).align_to(expl, LEFT)
        self.play(Create(ring), FadeIn(note))
        self.wait(1.5)
        res = fit(T(f"Real best book, Q4 2025 (8 ETFs, 4 vs 4). At 16 ETFs, 8 vs 8: about "
                    f"{NUM['ls_median_optima_8x8_etf']} competing books per quarter, and greedy picks "
                    "the wrong one 4 times in 5.", 22, FG, "BOLD"), 13.2)\
            .to_edge(DOWN, buff=0.3)
        self.play(FadeOut(ring), Write(res))
        self.beat(14, notes=NOTES["best_book"])
        clear(self)

    # ---------------------------------------------- 6. our move: circuit + proposal heatmaps (~0:40)
    def slide6(self):
        h = heading("Our move keeps the count fixed and steers by score")
        self.play(Write(h))
        tick = DATA["tickers"][1:]  # hardware instance: SPY fixed long, one qubit per other ETF (7 qubits, 35 books)
        wires = VGroup(*[Line(LEFT * 5.6, RIGHT * 5.6, color=MUTED, stroke_width=2).shift(UP * (1.75 - k * 0.34))
                         for k in range(len(tick))])
        wl = VGroup(*[T(t, 16, MUTED).next_to(w, LEFT, buff=0.15) for t, w in zip(tick, wires)])
        self.play(Create(wires), FadeIn(wl), run_time=1.0)

        def block(x, color, label, tex, sub):
            box = RoundedRectangle(corner_radius=0.12, width=2.9, height=2.45, stroke_color=color, stroke_width=3,
                                   fill_color=color, fill_opacity=0.18).move_to(np.array([x, 0.7, 0]))
            inner = VGroup(T(label, 22, color, "BOLD"), fit(M(tex, 32, color), 2.6)).arrange(DOWN, buff=0.18)
            inner.move_to(box)
            back = BackgroundRectangle(inner, color=BG, fill_opacity=0.85, buff=0.08)
            return VGroup(box, back, inner, T(sub, 18, MUTED).next_to(box, DOWN, buff=0.15))

        mix1 = block(-3.6, QUANTUM, "Mix", r"M(\beta)", "XX+YY gates: try many\nlong-for-short trades at once")
        phase = block(0.0, CUT, "Score phase", r"P(\gamma) = e^{-i\gamma E(s)}", "RZ + RZZ gates: stamp\neach book with its score")
        mix2 = block(3.6, QUANTUM, "Mix, reversed", r"M(\beta)^{\text{rev}}", "recombine, then\nmeasure one book")
        self.play(LaggedStart(FadeIn(mix1, shift=DOWN * 0.2), FadeIn(phase, shift=DOWN * 0.2),
                              FadeIn(mix2, shift=DOWN * 0.2), lag_ratio=0.5), run_time=2.0)
        prop_tex = M(r"Q(s \to s') = \bigl|\langle s' \,|\, M(\beta)^{\text{rev}}\, P(\gamma)\, M(\beta) \,|\, s \rangle\bigr|^2"
                     r" = Q(s' \to s)", 34).move_to(np.array([0, -2.3, 0]))
        fixed = fit(T("Every gate trades a long for a short, so the book stays balanced (SPY is fixed long). The circuit is a "
                      "palindrome,\nso Q is symmetric and the plain Metropolis rule stays exact. Shown: 7 qubits, 35 books. "
                      "Main study: 11 qubits, C(11, 5) = 462 books.", 20, FG), 13.2).to_edge(DOWN, buff=0.3)
        self.play(Write(prop_tex), run_time=1.2)
        self.play(FadeIn(fixed))
        self.beat(8, notes=NOTES["circuit"])
        self.play(*[FadeOut(m) for m in (wires, wl, mix1, phase, mix2, prop_tex, fixed)], run_time=0.7)

        P = DATA["proposals"]
        left = heatmap_image(P["one_swap"], 3.6).move_to(LEFT * 3.3 + DOWN * 0.25)
        right = heatmap_image(P["quantum"], 3.6).move_to(RIGHT * 3.3 + DOWN * 0.25)
        to_l = T("to book →", 16, MUTED).next_to(left, UP, buff=0.08)
        to_r = T("to book →", 16, MUTED).next_to(right, UP, buff=0.08)
        fr_l = T("from book →", 16, MUTED).rotate(-PI / 2).next_to(left, LEFT, buff=0.1)
        fr_r = T("from book →", 16, MUTED).rotate(-PI / 2).next_to(right, LEFT, buff=0.1)
        lt = T("One swap", 26, CLASSICAL, "BOLD").next_to(to_l, UP, buff=0.12)
        rt = T("Quantum move", 26, QUANTUM, "BOLD").next_to(to_r, UP, buff=0.12)
        ls = T("only next-door books, all equally likely", 20, MUTED).next_to(left, DOWN, buff=0.2)
        rs = T("far-off books too, shaped by the scores", 20, MUTED).next_to(right, DOWN, buff=0.2)
        axis = fit(T("Each row: where the move can go from one book (books sorted worst to best). Brighter = more "
                     "likely;\nthe diagonal = staying put. Simulated, on the 35-book instance (8 ETFs, 4 vs 4) from "
                     "our hardware run.", 20, MUTED), 13.2).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(left), FadeIn(lt), FadeIn(to_l), FadeIn(fr_l), run_time=1.0)
        self.play(FadeIn(ls))
        self.play(FadeIn(right), FadeIn(rt), FadeIn(to_r), FadeIn(fr_r), run_time=1.0)
        self.play(FadeIn(rs), FadeIn(axis))
        self.beat(10, notes=NOTES["heatmaps"])
        clear(self)

    # ---------------------------------------------- 7. main result (~0:50)
    def slide7(self):
        h = heading(f"It explores faster than tuned, score-blind classical moves in "
                    f"{NUM['beats_multi_heldout']} of held-out quarters")
        self.play(Write(h))
        bars_data = NUM["bars_etf_fair"]
        colors = [CLASSICAL, CLASSICAL, QUANTUM]
        maxv, height, base_y, bw = 3.0, 2.2, -0.4, 1.0
        xs = [-5.9, -4.0, -2.1, -0.2]
        short = {"single swap": "one swap", "multi-swap (tuned)": "several swaps\n(tuned)",
                 "quantum (all-pairs mixer)": "quantum\nmove"}
        bars = VGroup(*[bar(v, maxv, height, bw, c, short[k], f"{v:.1f}" if k == "single swap" else f"{v:.2f}",
                            x, base_y) for (k, v), c, x in zip(bars_data.items(), colors, xs)])
        bars[0][2].shift(UP * 0.18)  # keep the "1.0" label clear of the reference line
        y1 = base_y + height / maxv
        one = DashedLine(np.array([xs[0] - 0.7, y1, 0]), np.array([xs[-1] + 0.7, y1, 0]), color=MUTED)
        self.play(*[GrowFromEdge(b[0], DOWN) for b in bars], *[FadeIn(b[1:]) for b in bars], Create(one), run_time=1.5)
        sub = fit(T("Exploration speed vs one swap (spectral-gap ratio)\n"
                    "ETFs, 6 vs 6, median over held-out quarters", 20, MUTED), 6.6)\
            .move_to(np.array([(xs[0] + xs[-1]) / 2, 2.35, 0]))
        metric = VGroup(
            M(r"\text{gap} = 1 - |\lambda_2(P)|", 32),
            T("exact, from each chain's full transition matrix P", 17, MUTED),
            T("one setting per method: tuned on even quarters, tested on odd", 17, MUTED),
        ).arrange(DOWN, buff=0.12)
        fit(metric, 5.8).move_to(np.array([3.9, 2.3, 0]))
        self.play(FadeIn(sub), FadeIn(metric))
        self.beat(4, notes=NOTES["bars"])

        # phase-off control: same circuit, score phase switched off, stays on screen as a fourth bar
        off_v = NUM["quantum_phase_off_etf"]
        off = bar(off_v, maxv, height, bw, BAD, "quantum,\nphase off", f"{off_v:.2f}", xs[3], base_y)
        ref = DashedLine(np.array([xs[1] - 0.7, base_y + height * bars_data["multi-swap (tuned)"] / maxv, 0]),
                         np.array([xs[3] + 0.7, base_y + height * bars_data["multi-swap (tuned)"] / maxv, 0]),
                         color=CLASSICAL, stroke_width=2)
        self.play(GrowFromEdge(off[0], DOWN), FadeIn(off[1:]), Create(ref), run_time=1.0)
        ctrl = fit(T("Switch off the score phase\nand it drops below the\ntuned classical move:\n"
                     "the gain comes from the score.", 26, GOOD), 5.4).move_to(np.array([3.9, 0.55, 0]))
        self.play(FadeIn(ctrl))
        self.beat(3, notes=NOTES["phase_off"])

        # per-quarter results grid
        PQ = DATA["per_quarter"]
        grid = VGroup()
        cell = 0.36
        for r, uni in enumerate(("ETFs", "stocks")):
            vals = PQ[uni]["ratio"]
            for c, v in enumerate(vals):
                t = min(abs(np.log(v)) / np.log(2.5), 1.0)
                col = GOOD if v > 1 else BAD
                sq = Square(cell, stroke_width=1, stroke_color=BG, fill_color=col, fill_opacity=0.25 + 0.75 * t)
                sq.move_to(np.array([-5.4 + c * cell, -1.95 - r * (cell + 0.12), 0]))
                grid.add(sq)
        row_l = VGroup(T("ETFs", 20, FG).next_to(grid[0], LEFT, buff=0.2),
                       T("stocks", 20, FG).next_to(grid[len(PQ["ETFs"]["ratio"])], LEFT, buff=0.2))
        wins = [np.mean(np.array(PQ[u]["ratio"]) > 1) for u in ("ETFs", "stocks")]
        row_r = VGroup(T(f"{wins[0]:.0%}", 22, GOOD, "BOLD").next_to(grid[len(PQ["ETFs"]["ratio"]) - 1], RIGHT, buff=0.2),
                       T(f"{wins[1]:.0%}", 22, GOOD, "BOLD").next_to(grid[-1], RIGHT, buff=0.2))
        q0, q1 = PQ["ETFs"]["quarters"][0][:4], PQ["ETFs"]["quarters"][-1][:4]
        cap = fit(T(f"Every held-out quarter, {q0} to {q1}: green = quantum explored faster than the tuned "
                    "several-swap move, red = slower. Brighter = bigger gap.", 18, MUTED), 13.0).to_edge(DOWN, buff=0.2)
        self.play(LaggedStart(*[FadeIn(s) for s in grid], lag_ratio=0.02), FadeIn(row_l), run_time=2.0)
        self.play(FadeIn(row_r), FadeIn(cap))
        self.beat(12, notes=NOTES["grid"])
        clear(self)

    # ---------------------------------------------- 8. limits, per the outline (~0:30)
    def slide8(self):
        h = heading("It's a sampling win, in simulation, and too deep for today's hardware")
        self.play(Write(h))
        race = NUM["race_etf_8x8"]

        def tile(mark, color, title, body):
            box = RoundedRectangle(corner_radius=0.15, width=4.2, height=4.0, stroke_color=color, stroke_width=3,
                                   fill_color=color, fill_opacity=0.08)
            m = T(mark, 48, color, "BOLD")
            t = fit(T(title, 26, color, "BOLD"), 3.8)
            b = fit(T(body, 22, FG), 3.8)
            content = VGroup(m, t, b).arrange(DOWN, buff=0.25).move_to(box)
            return VGroup(box, content)

        tiles = VGroup(
            tile("✓", GOOD, "A sampling win", "It explores the space of\ngood books faster, which is\n"
                                              "what you want for robust\npositions and real alternatives."),
            tile("✗", BAD, "Not a faster optimizer", f"To reach the single best book\n(16 ETFs, 8 vs 8), plain\n"
                                                     f"swaps get there first:\n{race['single swap']:,} vs "
                                                     f"{race['quantum']:,} steps."),
            tile("✗", BAD, "Not on today's hardware", f"The winning circuit needs\n~{NUM['winner_2q_gates']} two-qubit gates. "
                                                      f"Our cheap\nversion ran on ibm_marrakesh\nbut mixed slower than one swap."),
        ).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.1)
        for tl in tiles:
            self.play(FadeIn(tl, shift=UP * 0.2), run_time=0.7)
        fence = T("Not a speedup claim: a sampling result on the right kind of problem.", 24, MUTED)\
            .to_edge(DOWN, buff=0.35)
        self.play(FadeIn(fence))
        self.beat(14, notes=NOTES["limits"])

        # second build: why a quantum move at all (score-steered AND long-range), and where classical still wins
        self.play(FadeOut(tiles), FadeOut(fence), run_time=0.5)
        b = NUM["bars_etf_fair"]
        lb = NUM["locally_balanced_etf"]
        why = table([
            ["One swap", "No", "No", "1", f"{b['single swap']:.2f}"],
            ["Several swaps (tuned)", "No", "Yes", "1", f"{b['multi-swap (tuned)']:.2f}"],
            ["Locally balanced swap", "Yes", "No", f"{NUM['locally_balanced_checks']}", f"{lb:.2f}"],
            ["Quantum move", "Yes", "Yes", "1 circuit + 1", f"{b['quantum (all-pairs mixer)']:.2f}"],
        ], ["Move (ETFs, 6 vs 6)", "Steers by score?", "Jumps far?", "Score checks per step", "Speed vs one swap"],
            26, highlight=4)
        fit(why, 13.2).next_to(h, DOWN, buff=0.9)
        self.play(FadeIn(why), run_time=0.8)
        take = VGroup(
            T("Classically you can steer by score or jump far. Doing both means scoring", 24, FG),
            T("a combinatorially large set of books. The quantum move does both in one circuit.", 24, FG),
            T(f"At our size (462 books) the local classical move still wins. The open question is scale.", 24, CUT),
        ).arrange(DOWN, buff=0.18)
        fit(take, 13.0).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(take[:2]))
        self.play(FadeIn(take[2]))
        self.beat(14, notes=NOTES["why_quantum"])
        clear(self)

    # ---------------------------------------------- 9. contributions (stays up for Q&A)
    def slide9(self):
        h = heading("What we contributed")
        self.play(Write(h))
        lines = VGroup(
            T("1.  Found where real portfolio landscapes get rugged: market-neutral long-short books.", 24, FG),
            T("2.  Built a quantum move that explores them faster than tuned, score-blind classical moves\n"
              "     (exact answers, held-out quarters).", 24, FG),
            T("3.  Traced the gain to the score phase, and ran the circuit end to end on IBM hardware.", 24, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit(lines, 12.8).move_to(UP * 0.4)
        for l in lines:
            self.play(FadeIn(l, shift=UP * 0.15), run_time=0.7)
        slogan = T(SLOGAN, 40, QUANTUM, "BOLD").to_edge(DOWN, buff=1.1)
        credit = T(f"{TEAM}: {MEMBERS}", 20, MUTED).to_edge(DOWN, buff=0.4)
        self.play(Write(slogan), run_time=1.2)
        self.play(FadeIn(credit))
        self.beat(12, notes=NOTES["contributions"])

    # ---------------------------------------------- backup (Q&A only)
    def backup(self):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        h = heading("Backup: the detailed numbers")
        self.play(Write(h))
        race = NUM["race_etf_8x8"]
        b = NUM["bars_etf_fair"]
        t0 = table([
            ["One swap", f"{b['single swap']:.2f}"],
            ["Several swaps, tuned", f"{b['multi-swap (tuned)']:.2f}"],
            ["Quantum move, all pairs", f"{b['quantum (all-pairs mixer)']:.2f}"],
            ["Quantum, score phase off", f"{NUM['quantum_phase_off_etf']:.2f}"],
            ["Locally balanced (30 checks/step)", f"{NUM['locally_balanced_etf']:.2f}"],
        ], ["Move (ETFs, 6 vs 6)", "Speed vs one swap"], 18, highlight=3)
        t1 = table([[k, f"{v:,}"] for k, v in race.items()],
                   ["Method (ETFs, 8 vs 8)", "Steps to best book"], 18)
        t2 = table([
            ["Usable shots", NUM["hw_usable"]],
            ["Mixing on hardware", f"{NUM['hw_gap']}"],
            ["Mixing, ideal circuit", f"{NUM['ideal_gap']}"],
            ["Mixing, one swap", f"{NUM['swap_gap']}"],
            ["QPU time", f"{NUM['hw_qpu_seconds']} s"],
        ], ["ibm_marrakesh, 4 vs 4", "Value"], 18)
        g = VGroup(t0, t1, t2).arrange(RIGHT, buff=0.45, aligned_edge=UP)
        fit(g, 13.4).next_to(h, DOWN, buff=0.9)
        self.play(FadeIn(t0), FadeIn(t1), FadeIn(t2), run_time=1.2)
        self.beat(10, notes=NOTES["backup"])


class Slide1Title(Talk):
    def construct(self):
        self.slide1()


class Slide2Walk(Talk):
    def construct(self):
        self.slide2()


class Slide3Landscape(Talk):
    def construct(self):
        self.slide3()


class Slide4MaxCut(Talk):
    def construct(self):
        self.slide4()


class Slide5Book(Talk):
    def construct(self):
        self.slide5()


class Slide6Move(Talk):
    def construct(self):
        self.slide6()


class Slide7Result(Talk):
    def construct(self):
        self.slide7()


class Slide8Limits(Talk):
    def construct(self):
        self.slide8()


class Slide9Contributions(Talk):
    def construct(self):
        self.slide9()


class Backup(Talk):
    def construct(self):
        self.backup()


SEQUENCE = ("slide1", "slide2", "slide3", "slide4", "slide5", "slide6", "slide7", "slide8", "slide9")


class FullTalk(Talk):
    def construct(self):
        for s in SEQUENCE:
            getattr(self, s)()


if ThreeDSlide is not None:

    class FullTalkSlides(ThreeDSlide, Talk):
        """Clickable slideshow with speaker notes; backup slide last."""

        def construct(self):
            for s in SEQUENCE + ("backup",):
                getattr(self, s)()
