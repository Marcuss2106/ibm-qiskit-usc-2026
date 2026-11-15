"""Five-minute talk: smarter moves for portfolio search.

Render (from presentation/, after `python make_data.py` has written data.json):
    manim -pql slides.py FullTalk                       # quick preview, timed video
    manim -qh  slides.py FullTalk                       # 1080p video
    manim-slides render --quality h slides.py FullTalkSlides && manim-slides present FullTalkSlides
Narration: narration.md. Numbers: data.json (from make_data.py) and ../research_results.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, ORIGIN, PI, RIGHT, UP, UR,
    ArcBetweenPoints, BackgroundRectangle, Circle, Create, DashedLine, Dot,
    FadeIn, FadeOut, Flash, FunctionGraph, GrowFromEdge, Indicate, LaggedStart, Line,
    ManimColor, MoveAlongPath, Rectangle, RoundedRectangle, Scene, Square, Table,
    Text, Transform, ValueTracker, VGroup, Write, always_redraw, config, interpolate_color,
)

try:  # optional: clickable slideshow via manim-slides
    from manim_slides import Slide
except ImportError:  # video rendering still works without it
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
    return fit(T(s, 40, FG, "BOLD")).to_edge(UP, buff=0.4)


def hill(x):
    return 2.4 * np.exp(-(x / 2.6) ** 2) - 1.6


def jagged(x):
    env = 1.1 * np.exp(-(x / 4.2) ** 2)
    return env + 0.42 * np.sin(2.3 * x) + 0.22 * np.sin(5.3 * x + 1.0) - 1.2


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
    if highlight is not None:
        t.get_rows()[highlight].set_color(hcolor)
    return t


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

    # ---------------------------------------------- 1. title (0:00-0:25)
    def slide1(self):
        title = fit(T("Smarter Moves for Portfolio Search", 50, FG, "BOLD"), 12.5)
        sub = fit(T("Using a small quantum circuit to steer a search through real ETF portfolios", 26, MUTED), 12.5)
        team = T("IBM Quantum x USC Hackathon 2026", 22, MUTED)
        VGroup(title, sub, team).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=1.4)
        self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(team, shift=UP * 0.2))
        self.beat(3)
        self.play(VGroup(title, sub, team).animate.scale(0.6).to_edge(UP, buff=0.3))

        curve = landscape(hill, color=MUTED).shift(DOWN * 0.7)
        self.play(Create(curve), run_time=1.0)
        tc = ValueTracker(-5.0)
        cdot = walker(hill, tc, CLASSICAL, shift=DOWN * 0.7)
        self.add(cdot)
        for x in (-4.4, -3.8, -3.2, -2.6):
            self.play(tc.animate.set_value(x), run_time=0.4)
        qdot = Dot(np.array([4.8, hill(4.8) - 0.7, 0]), radius=0.12, color=QUANTUM)
        path = ArcBetweenPoints(qdot.get_center(), np.array([0.3, hill(0.3) - 0.7, 0]), angle=-PI / 2)
        self.play(FadeIn(qdot))
        self.play(MoveAlongPath(qdot, path), run_time=1.1)
        self.play(Flash(qdot, color=QUANTUM))
        legend = VGroup(
            VGroup(Dot(color=CLASSICAL), T("the usual way: one small step at a time", 22, CLASSICAL)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=QUANTUM), T("our way: jumps steered by a quantum circuit", 22, QUANTUM)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR).shift(DOWN * 1.7)
        q = T("Can a quantum circuit suggest better moves?", 34, FG, "BOLD").to_edge(DOWN, buff=0.9)
        note = T("We kept every problem small enough to check every possible answer.", 22, MUTED)\
            .next_to(q, DOWN, buff=0.2)
        self.play(FadeIn(legend), Write(q))
        self.play(FadeIn(note))
        self.beat(10)
        clear(self)

    # ---------------------------------------------- 2. how the search works (0:25-1:10)
    def slide2(self):
        h = heading("How the search works")
        self.play(Write(h))
        tick = DATA["tickers"]

        def row(highlight, y=2.0):
            cells = VGroup()
            for i, t in enumerate(tick):
                on = i in highlight
                box = RoundedRectangle(corner_radius=0.08, width=1.05, height=0.62,
                                       stroke_color=LONG if on else MUTED, stroke_width=3,
                                       fill_color=LONG, fill_opacity=0.35 if on else 0.0)
                cells.add(VGroup(box, T(t, 20, FG if on else MUTED)))
            return cells.arrange(RIGHT, buff=0.12).move_to(UP * y)

        r = row({0, 1, 4, 6})
        count = T("4 held", 24, LONG).next_to(r, RIGHT, buff=0.3)
        intro = T("Start with a portfolio. Suggest a change. Keep it if it helps,\n"
                  "and every so often keep it even if it doesn't, so you never get stuck.", 24, MUTED)\
            .next_to(r, DOWN, buff=0.4)
        self.play(FadeIn(r), FadeIn(count))
        self.play(FadeIn(intro))
        self.wait(5)

        cl = T("The usual move swaps one holding for another.", 26, CLASSICAL).move_to(DOWN * 0.15)
        self.play(FadeIn(cl))
        self.play(Transform(r, row({0, 1, 3, 6})), run_time=1.0)
        self.play(Indicate(r[3], color=LONG), Indicate(r[4], color=MUTED), run_time=0.8)
        self.beat(5)
        self.play(FadeOut(cl))

        qt = T("Our move hands the choice to a circuit. It tries many trades at once,\n"
               "weighs each one by how good the result would be, and hands back one.", 24, QUANTUM)\
            .move_to(DOWN * 0.25)
        self.play(FadeIn(qt))
        options = [{0, 1, 3, 6}, {0, 2, 3, 6}, {0, 1, 3, 7}, {1, 3, 5, 6}, {0, 3, 4, 6}, {0, 1, 2, 3}]
        ghosts = VGroup(*[row(o).scale(0.42).set_opacity(0.45) for o in options])
        ghosts.arrange_in_grid(rows=3, cols=2, buff=(0.9, 0.2)).move_to(DOWN * 2.1)
        self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.3) for g in ghosts], lag_ratio=0.15), run_time=1.5)
        hands = VGroup()
        for g, sc in zip(ghosts, [0.9, 0.3, 0.7, 0.2, 0.8, 0.4]):
            c = Circle(radius=0.15, color=QUANTUM, stroke_width=2).next_to(g, LEFT, buff=0.12)
            hand = Line(c.get_center(), c.get_center() + 0.14 * np.array([np.cos(sc * 2 * PI), np.sin(sc * 2 * PI), 0]),
                        color=QUANTUM, stroke_width=3)
            hands.add(VGroup(c, hand))
        self.play(LaggedStart(*[FadeIn(hd) for hd in hands], lag_ratio=0.1), run_time=1.0)
        self.play(*[g.animate.set_opacity(0.9 if i == 0 else 0.12) for i, g in enumerate(ghosts)],
                  *[hd.animate.set_opacity(0.15) for hd in hands], run_time=1.0)
        self.play(Transform(r, row(options[0])), FadeOut(ghosts), FadeOut(hands), run_time=1.1)
        self.play(Indicate(count, color=LONG))
        foot = T("It always keeps four holdings, and everything else about the search stays the same,\n"
                 "so any difference we see comes from the move itself.", 22, FG).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(foot))
        self.beat(18)
        clear(self)

    # ---------------------------------------------- 3. most portfolios are one big hill (1:10-1:50)
    def slide3(self):
        h = heading("Most portfolio problems are one big hill")
        self.play(Write(h))
        left = landscape(hill, -3, 3, MUTED).scale(0.75).move_to(LEFT * 3.4 + UP * 1.45)
        right = landscape(lambda x: jagged(x * 1.6), -3, 3, MUTED).scale(0.75).move_to(RIGHT * 3.4 + UP * 1.45)
        lc = T("Real ETF data: every quarter we checked\nhad one best answer, and plain uphill\nsteps found it from anywhere.",
               20, GOOD).next_to(left, DOWN, buff=0.25)
        rc = T("Shuffle the correlations at random\nand you get about a dozen peaks.", 20, CUT)\
            .next_to(right, DOWN, buff=0.25)
        self.play(Create(left), run_time=1.0)
        d = Dot(left.point_from_proportion(0.05), color=CLASSICAL)
        self.play(FadeIn(d))
        self.play(MoveAlongPath(d, left.copy().pointwise_become_partial(left, 0.05, 0.5)), run_time=1.3)
        self.play(FadeIn(lc))
        self.beat(3)
        self.play(Create(right), run_time=1.0)
        self.play(FadeIn(VGroup(*[Dot(right.point_from_proportion(p), color=CLASSICAL) for p in (0.17, 0.41, 0.8)])),
                  FadeIn(rc))
        self.wait(2)

        corr = np.array(DATA["corr"])
        n = len(corr)
        cells = VGroup(*[
            Square(0.21, stroke_width=0.5, stroke_color=BG, fill_opacity=1,
                   fill_color=interpolate_color(COOL, WARM, (corr[i, j] + 1) / 2)).move_to(np.array([j * 0.21, -i * 0.21, 0]))
            for i in range(n) for j in range(n)
        ]).move_to(DOWN * 1.55 + LEFT * 3.0)
        hm = T("Why? Real correlations mostly lean the same way.\nWhen the market moves, nearly everything moves with it,\n"
               "so there's never a second good answer to compete.", 20, MUTED).next_to(cells, RIGHT, buff=0.35)
        self.play(FadeIn(cells), FadeIn(hm))
        self.wait(3)
        pivot = T("So we went looking for a problem where the market works against you.", 26, QUANTUM, "BOLD")\
            .to_edge(DOWN, buff=0.35)
        self.play(Write(pivot))
        self.beat(20)
        clear(self)

    # ---------------------------------------------- 4. max-cut with a cut line (1:50-2:30)
    def slide4(self):
        h = heading("Max-cut: draw a line, cut the heavy edges")
        rule = T("Split the nodes into two groups with a line. Every edge the line crosses\n"
                 "scores its weight. The goal is to cut as much weight as you can.", 22, MUTED)\
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
            line = DashedLine(centre - 2.1 * direction, centre + 2.1 * direction, color=CUT, stroke_width=5)
            total = sum(w for a, b, w in edges if sides[a] != sides[b])
            return sides, line, total

        cuts = sorted((cut_for(d) for d in (75, 15)), key=lambda c: c[2])  # weaker cut first
        cut_line, score = None, None
        for sides, line, total in cuts:
            anims = [nd.animate.set_color(LONG if s > 0 else SHORT) for nd, s in zip(nodes, sides)]
            anims += [ln.animate.set_color(CUT if sides[a] != sides[b] else MUTED)
                      .set_stroke(width=6 if sides[a] != sides[b] else 2) for ln, (a, b, _) in zip(lines, edges)]
            new_score = T(f"cut weight: {total}", 26, CUT, "BOLD").move_to(centre + DOWN * 2.15)
            if cut_line is None:
                cut_line, score = line, new_score
                self.play(Create(cut_line), *anims, FadeIn(score), run_time=1.2)
            else:
                self.play(Transform(cut_line, line), *anims, Transform(score, new_score), run_time=1.2)
            self.wait(1.5)
        better = T("A better line, a bigger score.", 22, GOOD).next_to(score, DOWN, buff=0.1)
        self.play(FadeIn(better))
        self.beat(2)

        # triangle: no line cuts all three edges
        tp = [RIGHT * 3.6 + UP * 0.55, RIGHT * 2.4 + DOWN * 1.3, RIGHT * 4.8 + DOWN * 1.3]
        tri_e = [(0, 1, 3), (1, 2, 4), (0, 2, 5)]
        tri_l = VGroup(*[Line(tp[a], tp[b], color=MUTED, stroke_width=4) for a, b, _ in tri_e])
        tri_w = VGroup(*[weight_label(str(w), (tp[a] + tp[b]) / 2, 18) for a, b, w in tri_e])
        tri_n = VGroup(*[Dot(p, radius=0.22, color=MUTED) for p in tp])
        tri_t = T("Now try three nodes that are all connected.", 22, FG).next_to(tri_n, UP, buff=0.3)
        self.play(Create(tri_l), FadeIn(tri_n), FadeIn(tri_w), FadeIn(tri_t))
        tcentre = sum(tp) / 3
        tri_line = None
        for normal_deg in (100, 20):
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
        frus = fit(T("However you draw the line, one edge stays uncut.\nThat tension is what makes max-cut hard.",
                     22, BAD), 5.6).move_to(np.array([3.6, -2.35, 0]))
        self.play(FadeIn(frus))
        foot = T("A graph full of triangles like this has lots of good, very different answers.", 24, FG)\
            .to_edge(DOWN, buff=0.25)
        self.play(FadeIn(foot))
        self.beat(21)
        clear(self)

    # ---------------------------------------------- 5. the long-short book is a max-cut (2:30-3:20)
    def slide5(self):
        h = heading("A long-short book is a max-cut in disguise")
        self.play(Write(h))
        tick = DATA["tickers"]
        corr = np.array(DATA["corr"])
        best = DATA["best_signs"]
        n = len(tick)
        centre = LEFT * 3.8 + DOWN * 0.35
        start = [centre + 2.0 * np.array([np.cos(a), np.sin(a), 0])
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
        for i, j in pairs:
            if abs(corr[i, j]) < 0.7:
                continue
            lab = weight_label(f"{corr[i, j]:.2f}", (start[i] + start[j]) / 2, 15)
            lab.add_updater(lambda m, i=i, j=j: m.move_to(0.5 * (dots[i].get_center() + dots[j].get_center())))
            wl.add(lab)
        self.add(lines, dots, names)
        self.play(*[Create(ln) for ln in lines], FadeIn(dots), FadeIn(names), run_time=1.4)
        self.play(FadeIn(wl))

        expl = VGroup(
            T("Every ETF is a node.", 22, FG),
            T("Edge weight is how closely two ETFs move together.", 22, WARM),
            T("Long or short is which side of the line you're on.", 22, LONG),
            T("Cutting a heavy edge puts two look-alike assets\non opposite sides, and that's exactly what\nmakes the book safer.", 22, CUT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        fit(expl, 6.2).move_to(RIGHT * 3.3 + UP * 1.15)
        for e in expl:
            self.play(FadeIn(e, shift=LEFT * 0.2), run_time=0.55)
        self.beat(5)

        cut = DashedLine(np.array([-3.8, 1.85, 0]), np.array([-3.8, -2.65, 0]), color=CUT, stroke_width=6)
        lab_l = T("long", 22, LONG, "BOLD").move_to(np.array([-5.4, 1.95, 0]))
        lab_s = T("short", 22, SHORT, "BOLD").move_to(np.array([-2.2, 1.95, 0]))
        self.play(FadeOut(wl), run_time=0.4)
        self.play(*[d.animate.move_to(p).set_color(LONG if best[i] > 0 else SHORT)
                    for i, (d, p) in enumerate(zip(dots, target))], run_time=2.0)
        self.play(Create(cut), FadeIn(lab_l), FadeIn(lab_s))
        crossing = [k for k, (i, j) in enumerate(pairs) if best[i] != best[j] and corr[i, j] > 0]
        self.play(*[lines[k].animate.set_color(CUT).set_stroke(opacity=0.95) for k in crossing], run_time=0.8)
        self.beat(2)

        tri = [tick.index(t) for t in ("SPY", "IWM", "EFA")]
        ring = VGroup(*[Circle(radius=0.45, color=CUT, stroke_width=4).move_to(dots[i]) for i in tri])
        note = fit(T("SPY, IWM and EFA all move together, so one pair\nalways ends up on the same side: "
                     "a frustrated triangle.", 20, CUT), 6.2).next_to(expl, DOWN, buff=0.4).align_to(expl, LEFT)
        self.play(Create(ring), FadeIn(note))
        self.wait(2)
        res = fit(T(f"On real data that makes a bumpy landscape: about {NUM['ls_median_optima_8x8_etf']} good-but-different\n"
                    "books in a typical quarter, and a greedy search picks the wrong one about 4 times in 5.",
                    22, FG, "BOLD"), 13.0).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(ring), Write(res))
        self.beat(26)
        clear(self)

    # ---------------------------------------------- 6. what the quantum move does (3:20-4:05)
    def slide6(self):
        h = heading("What the quantum move does here")
        self.play(Write(h))
        bars_data = NUM["bars_etf_fair"]
        colors = [CLASSICAL, CLASSICAL, QUANTUM]
        maxv, height, base_y, bw = 3.0, 2.6, -0.55, 1.1
        xs = [-6.1, -4.35, -2.6]
        short = {"single swap": "one swap", "multi-swap (tuned)": "several swaps\n(tuned)",
                 "quantum (all-pairs mixer)": "quantum\nmove"}
        bars = VGroup(*[bar(v, maxv, height, bw, c, short[k], f"{v:.1f}" if k == "single swap" else f"{v:.2f}",
                            x, base_y) for (k, v), c, x in zip(bars_data.items(), colors, xs)])
        y1 = base_y + height / maxv
        one = DashedLine(np.array([xs[0] - 0.8, y1, 0]), np.array([xs[-1] + 0.8, y1, 0]), color=MUTED)
        axis = T("How fast each move explores good books\n(ETFs, quarters held back from tuning)", 20, MUTED)\
            .next_to(bars, DOWN, buff=0.2)
        self.play(*[GrowFromEdge(b[0], DOWN) for b in bars], *[FadeIn(b[1:]) for b in bars],
                  Create(one), FadeIn(axis), run_time=1.6)
        call = fit(T(f"With a circuit that lets any pair of assets trade,\nthe quantum move explored faster than our\n"
                     f"best-tuned classical move in {NUM['beats_multi_heldout']} of quarters\nwe held back for testing.",
                     24, QUANTUM, "BOLD"), 6.4).to_edge(RIGHT, buff=0.45).shift(UP * 1.75)
        self.play(FadeIn(call))
        self.beat(4)

        q = bars[2]
        off_v = NUM["quantum_phase_off_etf"]
        on_rect, on_val = q[0].copy(), q[2].copy()
        off_rect = Rectangle(width=bw, height=height * off_v / maxv, fill_color=BAD, fill_opacity=0.9,
                             stroke_width=0).move_to(on_rect.get_bottom(), aligned_edge=DOWN)
        off_val = T(f"{off_v:.2f}", 26, BAD, "BOLD").next_to(off_rect, UP, buff=0.1)
        toggle = T("scores switched off", 20, BAD).next_to(off_val, UP, buff=0.12)
        self.play(FadeIn(toggle), Transform(q[0], off_rect), Transform(q[2], off_val), run_time=1.0)
        self.wait(1.5)
        self.play(FadeOut(toggle), Transform(q[0], on_rect), Transform(q[2], on_val), run_time=1.0)
        ok = fit(T("Switch off the part of the circuit that knows the scores\nand the edge goes away. "
                   "The speed-up really does come\nfrom the quantum step.", 23, GOOD), 6.4)\
            .next_to(call, DOWN, buff=0.4).align_to(call, LEFT)
        self.play(FadeIn(ok))
        self.beat(4)
        hw = fit(T(f"We also ran the circuit for real on IBM's\nMarrakesh processor: 35 starting books,\n"
                   f"1,024 shots each, about {NUM['hw_qpu_seconds']} seconds of QPU time.", 24, FG), 6.4)\
            .next_to(ok, DOWN, buff=0.45).align_to(call, LEFT)
        self.play(FadeIn(hw))
        self.beat(26)
        clear(self)

    # ---------------------------------------------- 7. what we learned: tables (4:05-4:40)
    def slide7(self):
        h = heading("What we learned")
        self.play(Write(h))
        t1_title = T("Where we looked", 26, MUTED, "BOLD")
        t1 = table([
            ["Picking 5 of 16 ETFs", "1", "No"],
            ["Choosing factors to explain SPY", "1", "No"],
            ["Multi-asset hedge book", "1", "No"],
            ["Long-short book, 8 vs 8", str(NUM["ls_median_optima_8x8_etf"]), "Yes"],
        ], ["Problem", "Peaks in a typical quarter", "Room for a smarter move?"], 22, highlight=4)
        g1 = fit(VGroup(t1_title, t1).arrange(DOWN, buff=0.25), 12.8).move_to(DOWN * 0.1)
        self.play(FadeIn(t1_title), Create(t1), run_time=1.6)
        self.beat(10)
        self.play(FadeOut(g1))

        t2_title = T("How fast each move explores (ETFs, held-out quarters)", 26, MUTED, "BOLD")
        b = NUM["bars_etf_fair"]
        t2 = table([
            ["One swap at a time", f"{b['single swap']:.2f}", "baseline"],
            ["Several swaps, tuned", f"{b['multi-swap (tuned)']:.2f}", "-"],
            ["Quantum move, all pairs", f"{b['quantum (all-pairs mixer)']:.2f}", f"{NUM['beats_multi_heldout']} of quarters"],
        ], ["Move", "Speed vs one swap", "Beats the tuned classical move"], 22, highlight=3)
        g2 = fit(VGroup(t2_title, t2).arrange(DOWN, buff=0.25), 12.8).move_to(UP * 0.3)
        self.play(FadeIn(t2_title), Create(t2), run_time=1.6)
        caveat = fit(T("Two honest caveats: for finding the single best book, plain swaps still get there first,\n"
                       "and on today's hardware the noise cancels out the gain.", 20, MUTED), 12.8)\
            .next_to(g2, DOWN, buff=0.45)
        self.play(FadeIn(caveat))
        self.beat(18)
        clear(self)

    # ---------------------------------------------- 8. where this leaves us (4:40-5:00)
    def slide8(self):
        h = heading("Where this leaves us")
        self.play(Write(h))
        left = landscape(hill, -3, 3, MUTED).scale(0.6).move_to(LEFT * 3.6 + UP * 1.3)
        right = landscape(lambda x: jagged(x * 1.6), -3, 3, QUANTUM).scale(0.6).move_to(RIGHT * 3.6 + UP * 1.3)
        ll = T("smooth problems", 20, MUTED).next_to(left, DOWN, buff=0.15)
        rl = T("tangled problems", 20, QUANTUM).next_to(right, DOWN, buff=0.15)
        self.play(Create(left), Create(right), FadeIn(ll), FadeIn(rl), run_time=1.1)
        lines = VGroup(
            T("Quantum moves pay off when a problem is tangled: lots of good answers pulling different ways.", 22, FG),
            T("Market-neutral long-short books are a real, everyday example of that kind of problem.", 22, FG),
            T("As hardware gets quieter, these are the problems worth running on it.", 22, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit(lines, 12.6).move_to(DOWN * 0.85)
        for l in lines:
            self.play(FadeIn(l, shift=UP * 0.15), run_time=0.7)
        close = fit(T("Find the tangled problems, and give the search a smarter move.", 32, QUANTUM, "BOLD"), 12.6)\
            .to_edge(DOWN, buff=0.45)
        self.play(Write(close), run_time=1.3)
        self.beat(13)
        clear(self)

    # ---------------------------------------------- backup (Q&A only)
    def backup(self):
        h = heading("Backup: the detailed numbers")
        self.play(Write(h))
        race = NUM["race_etf_8x8"]
        t1 = table([[k, f"{v:,}"] for k, v in race.items()],
                   ["Method (ETFs, 8 vs 8)", "Median steps to the best book"], 20)
        t2 = table([
            ["Usable shots", NUM["hw_usable"]],
            ["Mixing speed on hardware", f"{NUM['hw_gap']}"],
            ["Mixing speed, ideal circuit", f"{NUM['ideal_gap']}"],
            ["Mixing speed, one swap", f"{NUM['swap_gap']}"],
            ["QPU time", f"{NUM['hw_qpu_seconds']} s"],
        ], ["IBM Marrakesh, 4 vs 4", "Value"], 20)
        g = VGroup(t1, t2).arrange(RIGHT, buff=0.7, aligned_edge=UP)
        fit(g, 13.2).move_to(DOWN * 0.2)
        self.play(Create(t1), Create(t2), run_time=1.6)
        self.beat(10)


class Slide1Title(Talk):
    def construct(self):
        self.slide1()


class Slide2Search(Talk):
    def construct(self):
        self.slide2()


class Slide3Hill(Talk):
    def construct(self):
        self.slide3()


class Slide4MaxCut(Talk):
    def construct(self):
        self.slide4()


class Slide5Book(Talk):
    def construct(self):
        self.slide5()


class Slide6Quantum(Talk):
    def construct(self):
        self.slide6()


class Slide7Learned(Talk):
    def construct(self):
        self.slide7()


class Slide8Close(Talk):
    def construct(self):
        self.slide8()


class Backup(Talk):
    def construct(self):
        self.backup()


SEQUENCE = ("slide1", "slide2", "slide3", "slide4", "slide5", "slide6", "slide7", "slide8")


class FullTalk(Talk):
    def construct(self):
        for s in SEQUENCE:
            getattr(self, s)()


if Slide is not None:

    class FullTalkSlides(Slide, Talk):
        """Clickable slideshow: same slides, advances on click/arrow key; backup slide last."""

        def construct(self):
            for s in SEQUENCE + ("backup",):
                getattr(self, s)()
