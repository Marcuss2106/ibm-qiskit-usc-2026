"""Five-minute talk: Where can quantum search help in finance?

Render (from presentation/, after `python make_data.py` has written data.json):
    manim -pql slides.py FullTalk        # quick preview, whole talk
    manim -qh  slides.py FullTalk        # 1080p final
    manim -pql slides.py Slide5Morph     # one slide
Narration and timings: narration.md. Numbers: data.json (from make_data.py) and
../research_results.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, ORIGIN, PI, RIGHT, UP, UL, UR,
    AnimationGroup, ArcBetweenPoints, Arrow, Circle, Circumscribe, Create, CurvedArrow,
    DashedLine, Dot, FadeIn, FadeOut, Flash, FunctionGraph, GrowFromEdge, Indicate,
    LaggedStart, Line, MathTex, MoveAlongPath, Rectangle, RoundedRectangle, Scene,
    Square, Text, Transform, ValueTracker, VGroup, Write, always_redraw, config,
    interpolate_color, ManimColor,
)

try:  # optional: clickable slideshow via manim-slides
    from manim_slides import Slide
except ImportError:  # video-only rendering still works without it
    Slide = None

DATA = json.loads((Path(__file__).with_name("data.json")).read_text())
NUM = DATA["numbers"]

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
    return fit(T(s, 40, FG, "BOLD")).to_edge(UP, buff=0.45)


def hill(x):
    return 2.4 * np.exp(-(x / 2.6) ** 2) - 1.6


def jagged(x):
    env = 1.1 * np.exp(-(x / 4.2) ** 2)
    return env + 0.42 * np.sin(2.3 * x) + 0.22 * np.sin(5.3 * x + 1.0) - 1.2


def landscape(f, x0=-6, x1=6, color=FG, width=4):
    return FunctionGraph(f, x_range=[x0, x1, 0.02], color=color, stroke_width=width)


def walker(f, tracker, color, scale=1.0, shift=ORIGIN, radius=0.12):
    return always_redraw(
        lambda: Dot(np.array([tracker.get_value() * scale, f(tracker.get_value()) * scale, 0]) + shift,
                    radius=radius, color=color)
    )


def bar(value, max_value, height, width, color, label, value_label, x, base_y):
    """Bar whose bottom edge sits at (x, base_y), with label below and value above."""
    h = height * value / max_value
    rect = Rectangle(width=width, height=h, fill_color=color, fill_opacity=0.9, stroke_width=0)
    rect.move_to(np.array([x, base_y, 0]), aligned_edge=DOWN)
    lab = T(label, 20, MUTED).next_to(rect, DOWN, buff=0.15)
    val = T(value_label, 26, FG, "BOLD").next_to(rect, UP, buff=0.1)
    return VGroup(rect, lab, val)


def clear(scene):
    for m in scene.mobjects:
        m.clear_updaters()
    scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=0.6)


# ---------------------------------------------------------------- slides
class Talk(Scene):
    def beat(self, seconds: float):
        """Hold point: timed wait in the video, click-to-advance in the slideshow."""
        if Slide is not None and isinstance(self, Slide):
            self.next_slide()
        else:
            self.wait(seconds)

    # ---------------------------------------------- 1. title and question (0:00-0:30)
    def slide1(self):
        title = fit(T("Where Can Quantum Search Help in Finance?", 48, FG, "BOLD"), 12.5)
        sub = fit(T("Quantum-enhanced MCMC on real portfolio problems, measured against the exact answer", 24, MUTED), 12.5)
        team = T("IBM Quantum x USC Hackathon 2026", 22, MUTED)
        VGroup(title, sub, team).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(team, shift=UP * 0.2))
        self.beat(3)
        self.play(VGroup(title, sub, team).animate.scale(0.6).to_edge(UP, buff=0.3))

        curve = landscape(hill, color=MUTED).shift(DOWN * 0.6)
        self.play(Create(curve), run_time=1.2)
        tc = ValueTracker(-5.0)
        cdot = walker(hill, tc, CLASSICAL, shift=DOWN * 0.6)
        self.add(cdot)
        for x in (-4.4, -3.8, -3.2, -2.6, -2.0):
            self.play(tc.animate.set_value(x), run_time=0.45)
        qdot = Dot(np.array([4.8, hill(4.8) - 0.6, 0]), radius=0.12, color=QUANTUM)
        path = ArcBetweenPoints(qdot.get_center(), np.array([0.3, hill(0.3) - 0.6, 0]), angle=-PI / 2)
        self.play(FadeIn(qdot))
        self.play(MoveAlongPath(qdot, path), run_time=1.2)
        self.play(Flash(qdot, color=QUANTUM))
        legend = VGroup(
            VGroup(Dot(color=CLASSICAL), T("classical: small steps", 22, CLASSICAL)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=QUANTUM), T("quantum: score-guided jumps", 22, QUANTUM)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR).shift(DOWN * 1.6)
        q = T("Can a quantum circuit propose smarter moves?", 34, FG, "BOLD").to_edge(DOWN, buff=0.5)
        self.play(FadeIn(legend), Write(q))
        self.beat(14)
        clear(self)

    # ---------------------------------------------- 2. how the search works (0:30-1:20)
    def slide2(self):
        h = heading("The search: propose, accept or reject, repeat")
        self.play(Write(h))
        tick = DATA["tickers"]
        held = {0, 1, 4, 6}

        def row(highlight, y=1.6):
            cells = VGroup()
            for i, t in enumerate(tick):
                on = i in highlight
                box = RoundedRectangle(corner_radius=0.08, width=1.05, height=0.62,
                                       stroke_color=LONG if on else MUTED, stroke_width=3,
                                       fill_color=LONG, fill_opacity=0.35 if on else 0.0)
                cells.add(VGroup(box, T(t, 20, FG if on else MUTED)))
            return cells.arrange(RIGHT, buff=0.12).move_to(UP * y)

        r = row(held)
        loop_lab = T("propose  ->  accept or reject  ->  repeat", 24, MUTED).next_to(r, DOWN, buff=0.45)
        count = T("4 held", 24, LONG).next_to(r, RIGHT, buff=0.3)
        self.play(FadeIn(r), FadeIn(count))
        self.play(FadeIn(loop_lab))
        self.wait(5)

        # classical move: swap one out, one in
        cl_box = T("Classical move: swap one asset out, one in", 26, CLASSICAL).move_to(DOWN * 0.9)
        self.play(FadeIn(cl_box))
        self.play(Transform(r, row({0, 1, 3, 6})), run_time=1.0)
        self.play(Indicate(r[3], color=LONG), Indicate(r[4], color=MUTED), run_time=0.8)
        self.beat(5)
        self.play(FadeOut(cl_box))

        # quantum move: spread, score, recombine
        q_box = T("Quantum move:  spread  ->  score  ->  recombine", 26, QUANTUM).move_to(DOWN * 0.9)
        self.play(FadeIn(q_box))
        options = [{0, 1, 3, 6}, {0, 2, 3, 6}, {0, 1, 3, 7}, {1, 3, 5, 6}, {0, 3, 4, 6}, {0, 1, 2, 3}]
        ghosts = VGroup(*[row(o).scale(0.42).set_opacity(0.45) for o in options])
        ghosts.arrange_in_grid(rows=3, cols=2, buff=(0.9, 0.22)).move_to(DOWN * 2.35)
        self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.3) for g in ghosts], lag_ratio=0.15), run_time=1.6)
        scores = [0.9, 0.3, 0.7, 0.2, 0.8, 0.4]
        hands = VGroup()
        for g, sc in zip(ghosts, scores):
            c = Circle(radius=0.16, color=QUANTUM, stroke_width=2).next_to(g, LEFT, buff=0.12)
            hand = Line(c.get_center(), c.get_center() + 0.15 * np.array([np.cos(sc * 2 * PI), np.sin(sc * 2 * PI), 0]),
                        color=QUANTUM, stroke_width=3)
            hands.add(VGroup(c, hand))
        self.play(LaggedStart(*[FadeIn(hd) for hd in hands], lag_ratio=0.1), run_time=1.2)
        best = 0
        self.play(*[g.animate.set_opacity(0.9 if i == best else 0.12) for i, g in enumerate(ghosts)],
                  *[hd.animate.set_opacity(0.15) for hd in hands], run_time=1.2)
        self.play(Transform(r, row(options[best])), FadeOut(ghosts), FadeOut(hands), run_time=1.2)
        self.play(Indicate(count, color=LONG))
        foot = T("Same search, same answer key. Only the proposal changes.", 26, FG).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(foot))
        self.beat(23)
        clear(self)

    # ---------------------------------------------- 3. real portfolios are too easy (1:20-2:20)
    def slide3(self):
        h = heading("Surprise: real portfolio selection has one peak")
        self.play(Write(h))
        left = landscape(hill, -3, 3, MUTED).scale(0.8).move_to(LEFT * 3.4 + UP * 1.35)
        right = landscape(lambda x: jagged(x * 1.6), -3, 3, MUTED).scale(0.8).move_to(RIGHT * 3.4 + UP * 1.35)
        ll = T("Real ETF data", 26, FG, "BOLD").next_to(left, UP, buff=0.3)
        rl = T("Random correlations", 26, FG, "BOLD").next_to(right, UP, buff=0.3)
        lc = T(f"1 local optimum in {NUM['mv_one_optimum_windows']} quarters", 22, GOOD).next_to(left, DOWN, buff=0.3)
        rc = T(f"median {NUM['random_corr_median_optima']} local optima", 22, BAD).next_to(right, DOWN, buff=0.3)
        self.play(Create(left), FadeIn(ll), run_time=1.2)
        d = Dot(left.point_from_proportion(0.05), color=CLASSICAL)
        self.play(FadeIn(d))
        self.play(MoveAlongPath(d, left.copy().pointwise_become_partial(left, 0.05, 0.5)), run_time=1.5)
        self.play(FadeIn(lc))
        self.wait(2)
        self.play(Create(right), FadeIn(rl), run_time=1.2)
        stuck = VGroup(*[Dot(right.point_from_proportion(p), color=CLASSICAL) for p in (0.17, 0.41, 0.8)])
        self.play(FadeIn(stuck), FadeIn(rc))
        self.beat(3)

        # correlation heat map: almost all warm = one market factor
        corr = np.array(DATA["corr"])
        n = len(corr)
        cells = VGroup()
        for i in range(n):
            for j in range(n):
                c = corr[i, j]
                col = interpolate_color(COOL, WARM, (c + 1) / 2)
                cells.add(Square(0.22, stroke_width=0.5, stroke_color=BG, fill_color=col, fill_opacity=1)
                          .move_to(np.array([j * 0.22, -i * 0.22, 0])))
        cells.move_to(DOWN * 1.55 + LEFT * 2.6)
        hm_lab = T("Real ETF correlations: mostly warm\n= one market factor moves everything", 22, MUTED)\
            .next_to(cells, RIGHT, buff=0.35)
        self.play(FadeIn(cells), FadeIn(hm_lab))
        self.wait(3)
        b = T(f"Quantum vs classical exploration speed on real data: {NUM['mv_quantum_vs_swap']}", 24, BAD, "BOLD")\
            .to_edge(DOWN, buff=0.25)
        self.play(Write(b))
        tag = T("Same with stocks, factor models and hedge books", 22, MUTED).next_to(b, UP, buff=0.15)
        self.play(FadeIn(tag))
        self.beat(38)
        clear(self)

    # ---------------------------------------------- 4. max-cut and frustration (2:20-3:00)
    def slide4(self):
        h = heading("Hard problems look like max-cut")
        rule = T("Colour the nodes so connected nodes get different colours", 26, MUTED).next_to(h, DOWN, buff=0.25)
        self.play(Write(h), FadeIn(rule))
        pos = [np.array([np.cos(a), np.sin(a), 0]) * 1.8 + LEFT * 3.2 + DOWN * 0.4
               for a in np.linspace(PI / 2, PI / 2 + 2 * PI, 6, endpoint=False)]
        edges = [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (3, 5)]
        nodes = VGroup(*[Dot(p, radius=0.22, color=MUTED) for p in pos])
        lines = VGroup(*[Line(pos[a], pos[b], color=MUTED, stroke_width=3) for a, b in edges])
        self.play(Create(lines), FadeIn(nodes))
        colours = [LONG, SHORT, LONG, SHORT, LONG, SHORT]
        cut_count = ValueTracker(0)
        counter = always_redraw(lambda: T(f"edges cut: {int(cut_count.get_value())}", 24, CUT)
                                .next_to(nodes, DOWN, buff=0.4))
        self.add(counter)
        assigned = {}
        for i, col in enumerate(colours):
            assigned[i] = col
            anims = [nodes[i].animate.set_color(col)]
            for k, (a, b) in enumerate(edges):
                if a in assigned and b in assigned and i in (a, b) and assigned[a] != assigned[b]:
                    anims.append(lines[k].animate.set_color(CUT).set_stroke(width=6))
                    cut_count.increment_value(1)
            self.play(*anims, run_time=0.45)
        self.beat(1)

        # frustrated triangle on the right
        tp = [RIGHT * 3.4 + UP * 0.9, RIGHT * 2.2 + DOWN * 1.1, RIGHT * 4.6 + DOWN * 1.1]
        tri_l = VGroup(*[Line(tp[a], tp[b], color=MUTED, stroke_width=4) for a, b in ((0, 1), (1, 2), (0, 2))])
        tri_n = VGroup(*[Dot(p, radius=0.24, color=MUTED) for p in tp])
        tri_lab = T("three mutually connected nodes", 22, MUTED).next_to(tri_n, DOWN, buff=0.35)
        self.play(Create(tri_l), FadeIn(tri_n), FadeIn(tri_lab))
        for cols, uncut in (([LONG, SHORT, LONG], 2), ([LONG, LONG, SHORT], 0)):
            self.play(*[n.animate.set_color(c) for n, c in zip(tri_n, cols)], run_time=0.5)
            pairs = ((0, 1), (1, 2), (0, 2))
            self.play(*[tri_l[k].animate.set_color(CUT if cols[a] != cols[b] else BAD)
                        .set_stroke(width=7 if cols[a] != cols[b] else 4) for k, (a, b) in enumerate(pairs)],
                      run_time=0.5)
            self.play(Indicate(tri_l[uncut], color=BAD, scale_factor=1.15), run_time=0.8)
        frus = T("No colouring cuts all three: frustration", 26, BAD, "BOLD").next_to(tri_lab, DOWN, buff=0.25)
        self.play(Write(frus))
        foot = T("Frustration creates many competing near-best answers", 26, FG).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(foot))
        self.beat(25)
        clear(self)

    # ---------------------------------------------- 5. long-short book is max-cut (3:00-3:50)
    def slide5(self):
        h = heading("A market-neutral long-short book is a balanced max-cut")
        self.play(Write(h))
        tick = DATA["tickers"]
        corr = np.array(DATA["corr"])
        n = len(tick)
        centre = LEFT * 3.9 + DOWN * 0.2
        pos = [centre + 2.1 * np.array([np.cos(a), np.sin(a), 0])
               for a in np.linspace(PI / 2, PI / 2 + 2 * PI, n, endpoint=False)]
        lines, idx = VGroup(), []
        for i in range(n):
            for j in range(i + 1, n):
                c = corr[i, j]
                if abs(c) < 0.25:
                    continue
                lines.add(Line(pos[i], pos[j], color=WARM if c > 0 else COOL,
                               stroke_width=1 + 7 * abs(c), stroke_opacity=0.35 + 0.5 * abs(c)))
                idx.append((i, j))
        dots = VGroup(*[Dot(p, radius=0.34, color=MUTED) for p in pos])
        labels = VGroup(*[T(t, 18, BG, "BOLD").move_to(p) for t, p in zip(tick, pos)])
        self.play(Create(lines), FadeIn(dots), FadeIn(labels), run_time=1.5)

        mapping = VGroup(*[
            VGroup(T(a, 22, MUTED), T("->", 22, MUTED), T(b, 22, col)).arrange(RIGHT, buff=0.2)
            for a, b, col in (("node", "asset", FG), ("edge weight", "correlation", WARM),
                              ("colour", "long / short", LONG), ("equal colours", "market-neutral", FG),
                              ("cut", "lower risk", CUT))
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 3.4 + UP * 1.5)
        self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.2) for m in mapping], lag_ratio=0.25), run_time=2)

        # risk meter
        meter_bg = Rectangle(width=0.45, height=2.4, stroke_color=MUTED).move_to(LEFT * 0.6 + DOWN * 0.3)
        level = ValueTracker(DATA["risk_worst_norm"])
        fill = always_redraw(lambda: Rectangle(width=0.45, height=max(0.02, 2.4 * level.get_value()),
                                               stroke_width=0, fill_color=BAD, fill_opacity=0.85)
                             .align_to(meter_bg, DOWN).move_to(meter_bg.get_bottom(), aligned_edge=DOWN))
        mlab = T("book risk", 20, MUTED).next_to(meter_bg, UP, buff=0.12)
        self.play(FadeIn(meter_bg), FadeIn(mlab))
        self.add(fill)

        worst, best = DATA["worst_signs"], DATA["best_signs"]
        self.play(*[d.animate.set_color(LONG if s > 0 else SHORT) for d, s in zip(dots, worst)], run_time=0.8)
        self.wait(1)
        self.play(*[d.animate.set_color(LONG if s > 0 else SHORT) for d, s in zip(dots, best)],
                  level.animate.set_value(0.08), run_time=1.6)
        legend = VGroup(VGroup(Dot(color=LONG), T("long", 20, LONG)).arrange(RIGHT, buff=0.1),
                        VGroup(Dot(color=SHORT), T("short", 20, SHORT)).arrange(RIGHT, buff=0.1))\
            .arrange(RIGHT, buff=0.4).next_to(dots, DOWN, buff=0.15)
        self.play(FadeIn(legend))
        self.beat(2)

        # frustrated triangle: SPY, IWM, EFA all move together
        tri = [tick.index(t) for t in ("SPY", "IWM", "EFA")]
        tri_lines = VGroup(*[Line(pos[a], pos[b], color=CUT, stroke_width=8)
                             for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2]))])
        note = T("SPY, IWM, EFA all move together:\nthey cannot all sit on opposite sides", 22, CUT)\
            .next_to(mapping, DOWN, buff=0.5).align_to(mapping, LEFT)
        self.play(Create(tri_lines), FadeIn(note))
        self.play(Circumscribe(tri_lines, color=CUT), run_time=1.2)
        self.wait(2)
        res = fit(T(f"Real ETFs, 8 long / 8 short: median {NUM['ls_median_optima_8x8_etf']} local optima;"
                    f" greedy fails {NUM['ls_greedy_fail_8x8_etf']} of the time", 24, FG, "BOLD")).to_edge(DOWN, buff=0.3)
        formula = MathTex(r"\text{risk} \propto s^\top \Sigma s = \text{const} + 2\sum_{i<j}\Sigma_{ij}\,s_i s_j",
                          font_size=30, color=MUTED).next_to(note, DOWN, buff=0.45).align_to(note, LEFT)
        self.play(FadeOut(tri_lines), Write(res), FadeIn(formula))
        self.beat(30)
        clear(self)

    # ---------------------------------------------- 6. results (3:50-4:35)
    def slide6(self):
        h = heading("Results on real data (simulation, exact answers)")
        self.play(Write(h))
        bars_data = NUM["bars_etf_fair"]
        colors = [CLASSICAL, CLASSICAL, QUANTUM]
        maxv, height, base_y, bw = 3.0, 2.6, -0.55, 1.1
        xs = [-5.9, -4.3, -2.7]
        short = {"single swap": "single\nswap", "multi-swap (tuned)": "multi-swap\n(tuned)",
                 "quantum (all-pairs mixer)": "quantum\n(all pairs)"}
        bars = VGroup(*[bar(v, maxv, height, bw, c, short[k], f"{v:.1f}" if k == "single swap" else f"{v:.2f}",
                            x, base_y)
                        for (k, v), c, x in zip(bars_data.items(), colors, xs)])
        y1 = base_y + height / maxv
        one = DashedLine(np.array([xs[0] - 0.8, y1, 0]), np.array([xs[-1] + 0.8, y1, 0]), color=MUTED)
        one_lab = T("= single swap", 18, MUTED).next_to(one, RIGHT, buff=0.12)
        axis_lab = T("Exploration speed, ETFs, held-out quarters", 20, MUTED).next_to(bars, DOWN, buff=0.2)
        self.play(*[GrowFromEdge(b[0], DOWN) for b in bars], *[FadeIn(b[1:]) for b in bars],
                  Create(one), FadeIn(one_lab), FadeIn(axis_lab), run_time=1.6)
        call = T(f"Beats tuned classical long jumps\nin {NUM['beats_multi_heldout']} of held-out quarters",
                 24, QUANTUM, "BOLD").to_edge(RIGHT, buff=0.5).shift(UP * 2.1)
        self.play(FadeIn(call))
        self.beat(4)

        # phase-off control
        q = bars[2]
        off_v = NUM["quantum_phase_off_etf"]
        on_rect, on_val = q[0].copy(), q[2].copy()
        off_rect = Rectangle(width=bw, height=height * off_v / maxv, fill_color=BAD, fill_opacity=0.9,
                             stroke_width=0).move_to(on_rect.get_bottom(), aligned_edge=DOWN)
        off_val = T(f"{off_v:.2f}", 26, BAD, "BOLD").next_to(off_rect, UP, buff=0.1)
        toggle = T("score phase OFF", 22, BAD).next_to(off_val, UP, buff=0.15)
        self.play(FadeIn(toggle), Transform(q[0], off_rect), Transform(q[2], off_val), run_time=1.0)
        self.wait(1.5)
        self.play(FadeOut(toggle), Transform(q[0], on_rect), Transform(q[2], on_val), run_time=1.0)
        ok = fit(T("Phase off -> advantage disappears:\nthe gain is the quantum score information", 22, GOOD), 5.6)\
            .next_to(call, DOWN, buff=0.35).to_edge(RIGHT, buff=0.5)
        self.play(FadeIn(ok))
        self.beat(4)

        verdict = VGroup(
            T("✓  Explores good portfolios faster (sampling)", 22, GOOD),
            T("✗  Finds the single best faster: classical single swap still wins", 22, BAD),
            T(f"✗  Today's hardware: ran on IBM Marrakesh ({NUM['hw_qpu_seconds']} QPU-s); "
              f"noise halves its speed", 22, BAD),
            T(f"     cheap circuit {NUM['hw_2q_gates']} two-qubit gates; the winner needs ~{NUM['winner_2q_gates']}",
              19, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(DOWN, buff=0.3).to_edge(LEFT, buff=0.6)
        for v in verdict:
            self.play(FadeIn(v, shift=LEFT * 0.2), run_time=0.6)
        self.beat(25)
        clear(self)

    # ---------------------------------------------- 7. takeaways (4:35-5:00)
    def slide7(self):
        h = heading("Where quantum search can help, and where it can't")
        self.play(Write(h))
        left = landscape(hill, -3, 3, MUTED).scale(0.7).move_to(LEFT * 3.6 + UP * 0.9)
        right = landscape(lambda x: jagged(x * 1.6), -3, 3, MUTED).scale(0.7).move_to(RIGHT * 3.6 + UP * 0.9)
        lx = T("✗", 44, BAD).next_to(left, UP, buff=0.1)
        rx = T("✓", 44, GOOD).next_to(right, UP, buff=0.1)
        self.play(Create(left), Create(right), FadeIn(lx), FadeIn(rx), run_time=1.2)
        lines = VGroup(
            T("✓  Can help: frustrated problems with many competing good answers, used for sampling", 22, GOOD),
            T("✗  Can't yet: standard portfolio optimisation, finding one best answer, noisy hardware", 22, BAD),
            T("●  How we know: exact answers, fair classical baselines, held-out tuning, real hardware", 22, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        fit(lines, 12.6).move_to(DOWN * 1.1)
        for l in lines:
            self.play(Write(l), run_time=0.9)
        close = fit(T("We didn't find a speedup. We found where one could live.", 34, QUANTUM, "BOLD"), 12.6)\
            .to_edge(DOWN, buff=0.4)
        self.play(Write(close), run_time=1.4)
        self.beat(17)
        clear(self)

    # ---------------------------------------------- backup (not timed)
    def backup(self):
        h = heading("Backup: race to the best book and hardware run")
        self.play(Write(h))
        race = NUM["race_etf_8x8"]
        rows = VGroup(T("Median attempts to reach the best book (ETFs, 8 long / 8 short)", 24, FG, "BOLD"))
        for k, v in race.items():
            rows.add(T(f"{k:<20s} {v:>6,d}", 24, QUANTUM if k == "quantum" else FG, "NORMAL"))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(LEFT * 3.2 + UP * 0.2)
        hw = VGroup(
            T("IBM Marrakesh, 4 long / 4 short (35 books)", 24, FG, "BOLD"),
            T(f"usable shots {NUM['hw_usable']}", 24, FG),
            T(f"mixing: hardware {NUM['hw_gap']}  vs  ideal {NUM['ideal_gap']}", 24, FG),
            T(f"vs classical single swap {NUM['swap_gap']}", 24, FG),
            T(f"{NUM['hw_qpu_seconds']} QPU-seconds", 24, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 3.3 + UP * 0.2)
        self.play(FadeIn(rows), FadeIn(hw))
        self.beat(10)


class Slide1Title(Talk):
    def construct(self):
        self.slide1()


class Slide2Search(Talk):
    def construct(self):
        self.slide2()


class Slide3Surprise(Talk):
    def construct(self):
        self.slide3()


class Slide4MaxCut(Talk):
    def construct(self):
        self.slide4()


class Slide5Morph(Talk):
    def construct(self):
        self.slide5()


class Slide6Results(Talk):
    def construct(self):
        self.slide6()


class Slide7Takeaways(Talk):
    def construct(self):
        self.slide7()


class Backup(Talk):
    def construct(self):
        self.backup()


class FullTalk(Talk):
    def construct(self):
        for s in (self.slide1, self.slide2, self.slide3, self.slide4, self.slide5, self.slide6, self.slide7):
            s()


if Slide is not None:

    class FullTalkSlides(Slide, Talk):
        """Clickable slideshow: same slides, advances on click/arrow key; backup slide last."""

        def construct(self):
            for s in (self.slide1, self.slide2, self.slide3, self.slide4, self.slide5, self.slide6,
                      self.slide7, self.backup):
                s()
