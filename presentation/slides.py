"""Five-minute talk: rugged problems, quantum moves.

Follows docs/research/presentation-reference.md (assertion headlines, speaker notes,
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
    FadeIn, FadeOut, Flash, FunctionGraph, GrowFromEdge, ImageMobject, Indicate, LaggedStart,
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
            self.next_slide(notes=notes)
        else:
            self.wait(seconds)

    # ---------------------------------------------- 1. title and promise (~0:20)
    def slide1(self):
        title = fit(T(SLOGAN, 54, FG, "BOLD"), 12.5)
        sub = fit(T("Using a small quantum circuit to steer a search through real ETF portfolios", 26, MUTED), 12.5)
        team = T("IBM Quantum x USC Hackathon 2026", 22, MUTED)
        VGroup(title, sub, team).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=1.4)
        self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(team, shift=UP * 0.2))
        self.beat(3, notes="Open exactly: 'In five minutes you'll know where a quantum move actually "
                           "beats classical moves on a real finance problem, and where it doesn't.'")
        self.play(VGroup(title, sub, team).animate.scale(0.6).to_edge(UP, buff=0.3))

        curve = landscape(hill, color=MUTED).shift(DOWN * 0.7)
        self.play(Create(curve), run_time=1.0)
        tc = ValueTracker(-5.0)
        cdot = walker(hill, tc, CLASSICAL, shift=DOWN * 0.7)
        self.add(cdot)
        for x in (-4.4, -3.8, -3.2, -2.6):
            self.play(tc.animate.set_value(x), run_time=0.35)
        qdot = Dot(np.array([4.8, hill(4.8) - 0.7, 0]), radius=0.12, color=QUANTUM)
        path = ArcBetweenPoints(qdot.get_center(), np.array([0.3, hill(0.3) - 0.7, 0]), angle=-PI / 2)
        self.play(FadeIn(qdot))
        self.play(MoveAlongPath(qdot, path), run_time=1.1)
        self.play(Flash(qdot, color=QUANTUM))
        legend = VGroup(
            VGroup(Dot(color=CLASSICAL), T("classical: one small step at a time", 22, CLASSICAL)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=QUANTUM), T("quantum: jumps steered by the score", 22, QUANTUM)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR).shift(DOWN * 1.7)
        promise = T("Where does a quantum move actually beat classical moves?", 30, FG, "BOLD").to_edge(DOWN, buff=0.9)
        note = T("Every problem is small enough that we can check every possible answer.", 22, MUTED)\
            .next_to(promise, DOWN, buff=0.2)
        self.play(FadeIn(legend), Write(promise))
        self.play(FadeIn(note))
        self.beat(6, notes="We kept sizes small so every claim is measured against the true answer, "
                           "not estimated.")
        clear(self)

    # ---------------------------------------------- 2. the search is a walk (~0:25)
    def slide2(self):
        h = heading("Searching for a portfolio is a walk, one move at a time")
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

        r = row({0, 1, 4, 6})
        count = T("4 held", 24, LONG).next_to(r, RIGHT, buff=0.3)
        self.play(FadeIn(r), FadeIn(count))
        steps = VGroup(
            T("1. Suggest a change", 26, FG),
            T("2. Keep it if it helps", 26, FG),
            T("3. Sometimes keep it anyway, so you don't get stuck", 26, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(r, DOWN, buff=0.55)
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in steps], lag_ratio=0.4), run_time=1.6)
        self.wait(2)
        self.play(Transform(r, row({0, 1, 3, 6})), run_time=1.0)
        self.play(Indicate(r[3], color=LONG), Indicate(r[4], color=MUTED), run_time=0.8)
        cl = T("The usual move: swap one holding for another.", 26, CLASSICAL, "BOLD").to_edge(DOWN, buff=1.1)
        ours = T("We change only that move, and nothing else.", 26, QUANTUM, "BOLD").next_to(cl, DOWN, buff=0.25)
        self.play(FadeIn(cl))
        self.play(FadeIn(ours))
        self.beat(12, notes="MCMC in one sentence: propose, accept or reject, repeat. The proposal move is "
                            "the only thing we change, so any difference comes from the move.")
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
        lab = T(f"Long-only (pick 5 of 16 ETFs): {len(L['long_only'])} peak", 26, GOOD, "BOLD")\
            .to_corner(UR).shift(DOWN * 1.1 + LEFT * 0.2)
        self.add_fixed_in_frame_mobjects(lab)
        self.play(Create(lo), FadeIn(lab), run_time=2.0)
        self.beat(4, notes="Real ETF data, one quarter (ending 2022-06-30). One broad peak: plain uphill steps "
                           "reach the best portfolio from every start.")
        lab2 = T(f"Long-short (8 vs 8): {len(L['long_short'])} peaks", 26, CUT, "BOLD")\
            .to_corner(UR).shift(DOWN * 1.1 + LEFT * 0.2)
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
        self.beat(3, notes="Surprise: the famous problem is too easy. The market moves everything together, "
                           "so there's one answer. Flip to long-short and the same market creates many "
                           "competing answers. Rugged landscapes are where a smarter move can matter.")
        self.play(FadeOut(lo), FadeOut(lab2), FadeOut(key), run_time=0.8)
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1.0, run_time=1.0)

        t_title = T("Where we looked", 26, MUTED, "BOLD")
        t1 = table([
            ["Picking 5 of 16 ETFs", "1", "No"],
            ["Choosing factors to explain SPY", "1", "No"],
            ["Multi-asset hedge book", "1", "No"],
            ["Long-short book, 8 vs 8", str(len(L["long_short"])), "Yes"],
        ], ["Problem", "Peaks in a typical quarter", "Room for a smarter move?"], 22, highlight=4)
        g = fit(VGroup(t_title, t1).arrange(DOWN, buff=0.25), 12.6).move_to(DOWN * 0.3)
        self.add_fixed_in_frame_mobjects(g)
        self.play(FadeIn(t_title), Create(t1), run_time=1.6)
        self.beat(10, notes="We tried four real problems. Only the long-short book is rugged: in a typical "
                            "quarter about 13 good-but-different books, and greedy picks the wrong one "
                            "about 4 times in 5.")
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
            self.wait(1.2)
        better = T("Better line, bigger score.", 22, GOOD).next_to(score, DOWN, buff=0.1)
        self.play(FadeIn(better))
        self.beat(2, notes="This line scores 8. Move it and you get 15.")

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
        frus = fit(T("One edge always stays uncut.\nThat tension is what makes it hard.", 22, BAD), 5.6)\
            .move_to(np.array([3.6, -2.35, 0]))
        self.play(FadeIn(frus))
        foot = T("Lots of triangles means lots of good, very different answers.", 24, FG).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(foot))
        self.beat(12, notes="However you draw the line through a triangle, one edge stays uncut. Pile up "
                            "triangles and you get many good answers that look nothing alike.")
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
            T("Node = an ETF", 24, FG),
            T("Edge weight = how closely two ETFs move together", 24, WARM),
            T("Side of the line = long or short", 24, LONG),
            T("Cut a heavy edge = split two look-alikes = lower risk", 24, CUT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit(expl, 6.4).move_to(RIGHT * 3.3 + UP * 1.1)
        for e in expl:
            self.play(FadeIn(e, shift=LEFT * 0.2), run_time=0.5)
        self.beat(4, notes="Each ETF is a node; the number on an edge is the real correlation. Going long or "
                           "short is just which side of the line you're on.")

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
            .next_to(expl, DOWN, buff=0.45).align_to(expl, LEFT)
        self.play(Create(ring), FadeIn(note))
        self.wait(1.5)
        res = fit(T(f"Real best book, Q4 2025. Across quarters: about {NUM['ls_median_optima_8x8_etf']} "
                    "competing books, and greedy picks the wrong one 4 times in 5.", 22, FG, "BOLD"), 13.0)\
            .to_edge(DOWN, buff=0.3)
        self.play(FadeOut(ring), Write(res))
        self.beat(14, notes="This split is the real best book for the last quarter of 2025. Cutting heavy edges "
                            "puts look-alike assets on opposite sides, which is exactly what lowers risk.")
        clear(self)

    # ---------------------------------------------- 6. our move: circuit + proposal heatmaps (~0:40)
    def slide6(self):
        h = heading("Our move keeps the count fixed and steers by score")
        self.play(Write(h))
        n_w = 5
        wires = VGroup(*[Line(LEFT * 5.6, RIGHT * 5.6, color=MUTED, stroke_width=2).shift(UP * (1.4 - k * 0.55))
                         for k in range(n_w)])
        wl = VGroup(*[T(f"ETF {k + 1}", 18, MUTED).next_to(w, LEFT, buff=0.15) for k, w in enumerate(wires)])
        self.play(Create(wires), FadeIn(wl), run_time=1.0)

        def block(x, color, label, sub):
            box = RoundedRectangle(corner_radius=0.12, width=2.6, height=2.75, stroke_color=color, stroke_width=3,
                                   fill_color=color, fill_opacity=0.18).move_to(np.array([x, 0.3, 0]))
            return VGroup(box, T(label, 24, color, "BOLD").move_to(box), T(sub, 20, MUTED).next_to(box, DOWN, buff=0.2))

        mix1 = block(-3.4, QUANTUM, "Mix", "try many trades\nat once")
        phase = block(0.0, CUT, "Score\nphase", "weight each one\nby its score")
        mix2 = block(3.4, QUANTUM, "Mix\n(reversed)", "recombine, then\nmeasure one book")
        self.play(LaggedStart(FadeIn(mix1, shift=DOWN * 0.2), FadeIn(phase, shift=DOWN * 0.2),
                              FadeIn(mix2, shift=DOWN * 0.2), lag_ratio=0.5), run_time=2.0)
        fixed = T("Each gate only trades a long for a short, so the long/short count never changes.", 22, FG)\
            .to_edge(DOWN, buff=0.5)
        self.play(FadeIn(fixed))
        self.beat(6, notes="Mix, score phase, mix in reverse. The mixer only swaps a long for a short, so the "
                           "count is fixed. The phase is where the score steers the jump.")
        self.play(*[FadeOut(m) for m in (wires, wl, mix1, phase, mix2, fixed)], run_time=0.7)

        P = DATA["proposals"]
        left = heatmap_image(P["one_swap"], 3.6).move_to(LEFT * 3.3 + DOWN * 0.25)
        right = heatmap_image(P["quantum"], 3.6).move_to(RIGHT * 3.3 + DOWN * 0.25)
        lt = T("One swap", 26, CLASSICAL, "BOLD").next_to(left, UP, buff=0.25)
        rt = T("Quantum move", 26, QUANTUM, "BOLD").next_to(right, UP, buff=0.25)
        ls = T("only next-door books, all equally likely", 20, MUTED).next_to(left, DOWN, buff=0.2)
        rs = T("far-off books too, shaped by the scores", 20, MUTED).next_to(right, DOWN, buff=0.2)
        axis = T("Each row: where the move can go from one book (books sorted worst to best).\n"
                 "Brighter = more likely. Real 35-book instance from our hardware run.", 20, MUTED)\
            .to_edge(DOWN, buff=0.25)
        self.play(FadeIn(left), FadeIn(lt), run_time=1.0)
        self.play(FadeIn(ls))
        self.play(FadeIn(right), FadeIn(rt), run_time=1.0)
        self.play(FadeIn(rs), FadeIn(axis))
        self.beat(10, notes="Left: one swap can only reach the 12 neighbours of each book. Right: the quantum "
                            "move reaches far-off books, and how likely each jump is depends on the scores.")
        clear(self)

    # ---------------------------------------------- 7. main result (~0:50)
    def slide7(self):
        h = heading(f"It explores faster than tuned classical moves in {NUM['beats_multi_heldout']} of held-out quarters")
        self.play(Write(h))
        bars_data = NUM["bars_etf_fair"]
        colors = [CLASSICAL, CLASSICAL, QUANTUM]
        maxv, height, base_y, bw = 3.0, 2.2, -0.4, 1.0
        xs = [-6.1, -4.5, -2.9]
        short = {"single swap": "one swap", "multi-swap (tuned)": "several swaps\n(tuned)",
                 "quantum (all-pairs mixer)": "quantum\nmove"}
        bars = VGroup(*[bar(v, maxv, height, bw, c, short[k], f"{v:.1f}" if k == "single swap" else f"{v:.2f}",
                            x, base_y) for (k, v), c, x in zip(bars_data.items(), colors, xs)])
        y1 = base_y + height / maxv
        one = DashedLine(np.array([xs[0] - 0.7, y1, 0]), np.array([xs[-1] + 0.7, y1, 0]), color=MUTED)
        self.play(*[GrowFromEdge(b[0], DOWN) for b in bars], *[FadeIn(b[1:]) for b in bars], Create(one), run_time=1.5)
        sub = fit(T("Exploration speed vs one swap\n(ETFs, median over held-out quarters)", 20, MUTED), 4.6)\
            .move_to(np.array([-4.5, 2.35, 0]))
        self.play(FadeIn(sub))
        self.beat(4, notes=f"Main message. The quantum move explores about {bars_data['quantum (all-pairs mixer)']:.1f} "
                           "times faster than one swap, ahead of the best-tuned classical long jump.")

        # phase-off control
        q = bars[2]
        off_v = NUM["quantum_phase_off_etf"]
        on_rect, on_val = q[0].copy(), q[2].copy()
        off_rect = Rectangle(width=bw, height=height * off_v / maxv, fill_color=BAD, fill_opacity=0.9,
                             stroke_width=0).move_to(on_rect.get_bottom(), aligned_edge=DOWN)
        off_val = T(f"{off_v:.2f}", 26, BAD, "BOLD").next_to(off_rect, UP, buff=0.1)
        toggle = T("score phase off", 20, BAD).next_to(off_val, UP, buff=0.1)
        self.play(FadeIn(toggle), Transform(q[0], off_rect), Transform(q[2], off_val), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(toggle), Transform(q[0], on_rect), Transform(q[2], on_val), run_time=1.0)
        ctrl = fit(T("Switch off the score phase and the edge disappears:\nthe gain comes from the quantum step.",
                     22, GOOD), 6.2).move_to(np.array([3.4, 1.9, 0]))
        self.play(FadeIn(ctrl))
        self.beat(3, notes="The control: same circuit, score phase off. It falls back behind the classical "
                           "move. That's how we know the score phase does the work.")

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
                    "classical move, red = slower. Darker = bigger gap.", 18, MUTED), 13.0).to_edge(DOWN, buff=0.2)
        self.play(LaggedStart(*[FadeIn(s) for s in grid], lag_ratio=0.02), FadeIn(row_l), run_time=2.0)
        self.play(FadeIn(row_r), FadeIn(cap))
        self.beat(12, notes=f"Each square is one quarter we held back from tuning. Green wins: "
                            f"{wins[0]:.0%} of ETF quarters and {wins[1]:.0%} of stock quarters. "
                            f"Say the slogan: {SLOGAN}")
        clear(self)

    # ---------------------------------------------- 8. limits, per the outline (~0:30)
    def slide8(self):
        h = heading("It's a sampling win, in simulation, and too deep for today's hardware")
        self.play(Write(h))
        race = NUM["race_etf_8x8"]

        def tile(mark, color, title, body):
            box = RoundedRectangle(corner_radius=0.15, width=4.0, height=3.6, stroke_color=color, stroke_width=3,
                                   fill_color=color, fill_opacity=0.08)
            m = T(mark, 48, color, "BOLD")
            t = fit(T(title, 24, color, "BOLD"), 3.6)
            b = fit(T(body, 19, FG), 3.6)
            content = VGroup(m, t, b).arrange(DOWN, buff=0.25).move_to(box)
            return VGroup(box, content)

        tiles = VGroup(
            tile("✓", GOOD, "A sampling win", "It explores the space of\ngood books faster, which is\n"
                                              "what you want for robust\npositions and real alternatives."),
            tile("✗", BAD, "Not a faster optimizer", f"To reach the single best book,\nplain swaps get there first\n"
                                                     f"({race['single swap']:,} vs {race['quantum']:,} steps)."),
            tile("✗", BAD, "Not on today's hardware", f"The winning circuit needs\n~{NUM['winner_2q_gates']} two-qubit gates. "
                                                      f"Our cheap\nversion ran on ibm_marrakesh\nbut mixed slower than one swap."),
        ).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.2)
        for tl in tiles:
            self.play(FadeIn(tl, shift=UP * 0.2), run_time=0.7)
        fence = T("Not a speedup claim: a sampling result on the right kind of problem.", 24, MUTED)\
            .to_edge(DOWN, buff=0.35)
        self.play(FadeIn(fence))
        self.beat(14, notes="State the limits plainly; it protects the claim. Sampling, yes. Finding the single "
                            "best book faster, no. Hardware today, no: the winning circuit is about 540 two-qubit "
                            "gates, and our cheap version on ibm_marrakesh mixed slower than one swap.")
        clear(self)

    # ---------------------------------------------- 9. contributions (stays up for Q&A)
    def slide9(self):
        h = heading("What we contributed")
        self.play(Write(h))
        lines = VGroup(
            T("1.  Found where real portfolio landscapes get rugged: market-neutral long-short books.", 24, FG),
            T("2.  Built a quantum move that explores them faster than tuned classical moves\n"
              "     (exact answers, held-out quarters).", 24, FG),
            T("3.  Traced the gain to the score phase, and ran the circuit end to end on IBM hardware.", 24, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit(lines, 12.8).move_to(UP * 0.4)
        for l in lines:
            self.play(FadeIn(l, shift=UP * 0.15), run_time=0.7)
        slogan = T(SLOGAN, 40, QUANTUM, "BOLD").to_edge(DOWN, buff=0.8)
        self.play(Write(slogan), run_time=1.2)
        self.beat(12, notes="Restate the slogan, then a one-line salute to the audience. No 'Thank you / "
                            "Questions?' - leave this slide up for Q&A.")

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
        fit(g, 13.4).move_to(DOWN * 0.2)
        self.play(Create(t0), Create(t1), Create(t2), run_time=1.6)
        self.beat(10, notes="Backup for questions: speeds, race to the best book, hardware details.")


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
