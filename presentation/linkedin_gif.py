"""About 38-second silent loop for a LinkedIn post (4:5), our process end to end.

thumbnail (opening frame) -> data -> max-cut -> rugged landscape -> the move -> hardware -> result -> (loops to hook).
Reads data.json (talk numbers) and linkedin_data.json (prices, 16-ETF correlations, chip, hardware counts;
regenerate with `PYTHONPATH=. qiskit-env/bin/python presentation/linkedin_data.py`).

Render (from presentation/):
    .venv/bin/manim render -ql --resolution=540,676 --fps 15 linkedin_gif.py LinkedInLoop   # quick preview
    .venv/bin/manim render -qh --resolution=1080,1350 --fps 30 linkedin_gif.py LinkedInLoop
then make the GIF with the ffmpeg commands in README.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from manim import (
    DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UP,
    Create, CurvedArrow, DashedLine, Dot, FadeIn, FadeOut, GrowFromEdge,
    LaggedStart, Line, MoveAlongPath, ParametricFunction, Rectangle, RoundedRectangle,
    Sphere, Square, ThreeDAxes, ThreeDScene, Transform, VGroup, config, interpolate_color,
)

from slides import (
    BG, CLASSICAL, COOL, CUT, DATA, FG, GOOD, BAD, LONG, MUTED, NUM, QUANTUM, SHORT, WARM,
    T, fit, heatmap_image, peak_surface, side_of, weight_label,
)

sys.path.insert(0, str(Path(__file__).resolve().parent / "thumbnail"))
_px = (config.pixel_width, config.pixel_height)
import thumbnail as thumb  # noqa: E402  (the opening frame is the thumbnail)

config.pixel_width, config.pixel_height = _px  # thumbnail.py sets 1080x1350; keep the CLI resolution
config.frame_width = 8.0
config.frame_height = 10.0
config.background_color = BG

LD = json.loads((Path(__file__).with_name("linkedin_data.json")).read_text())
STEPS = ("data", "max-cut", "landscape", "move", "hardware", "result")
# pacing: holds (reading time) and animations are stretched from the 25 s cut
HOLD_PACE = 2.5
PLAY_PACE = 1.15
CAM = dict(phi=62 * DEGREES, theta=-58 * DEGREES)
CAM_2D = dict(**CAM, zoom=1.0, frame_center=ORIGIN)  # the landscape step's camera


def label(s, size=40, color=FG, y=4.25, width=7.4):
    """Headline label: bold, large enough for a phone feed."""
    return fit(T(s, size, color, "BOLD"), width).move_to(UP * y)


def corr_grid(c, height):
    """Correlation heat map: teal (negative) - background - red (positive)."""
    c = np.asarray(c)
    n = len(c)
    s = height / n
    g = VGroup()
    for i in range(n):
        for j in range(n):
            v = float(np.clip(c[i, j], -1, 1))
            col = interpolate_color(BG, WARM if v > 0 else COOL, abs(v) ** 0.8)
            g.add(Square(s, stroke_width=0, fill_opacity=1, fill_color=col).move_to(np.array([j * s, -i * s, 0])))
    return g


class LinkedInLoop(ThreeDScene):
    def play(self, *args, **kw):
        kw["run_time"] = kw.get("run_time", 1.0) * PLAY_PACE
        super().play(*args, **kw)

    def wait(self, duration=1.0, *args, **kw):
        super().wait(duration * HOLD_PACE, *args, **kw)

    def fx(self, *ms):
        """2D overlay: fixed in the frame while the camera stays tilted for the 3D landscapes."""
        self.add_fixed_in_frame_mobjects(*ms)
        return ms[0] if len(ms) == 1 else ms

    def progress(self, k):
        words = VGroup(*[T(w, 26, FG if i == k else MUTED, "BOLD" if i == k else "NORMAL")
                         for i, w in enumerate(STEPS)]).arrange(RIGHT, buff=0.3)
        fit(words, 7.6).move_to(DOWN * 4.55)
        dot = Dot(radius=0.05, color=QUANTUM).next_to(words[k], DOWN, buff=0.08)
        return VGroup(words, dot)

    def set_progress(self, k):
        new = self.progress(k)
        if getattr(self, "bar", None) is None:
            self.bar = self.fx(new)
            return [FadeIn(self.bar)]
        return [Transform(self.bar, new)]

    def construct(self):
        L = DATA["landscape3d"]
        self.axes = ThreeDAxes(x_range=[-1.3, 1.3], y_range=[-1.3, 1.3], z_range=[0, 1.2],
                               x_length=4.7, y_length=4.7, z_length=2.3).shift(DOWN * 0.2)
        self.bar = None
        self.hook()
        self.data_step()
        self.triangle_step()
        self.book_step()
        self.landscape_step(L)
        self.loop_step()
        self.proposal_step()
        self.hardware_step()
        self.result_step()

    # ------------------------------------------------------------ 0. opening = the thumbnail (also the loop's last frame)
    def hook(self):
        parts = thumb.build()
        self.set_camera_orientation(**parts["camera"])
        self.add(*parts["scene"])
        self.fx(parts["title"])
        self.wait(0.6)
        # a quantum walker retraces the thumbnail's jumps, ending on the best book
        paths = parts["paths"]
        walker = Sphere(paths[0](0), radius=0.1, resolution=(16, 16)).set_color(FG)
        self.play(FadeIn(walker), run_time=0.15)
        for path in paths:
            self.play(MoveAlongPath(walker, ParametricFunction(path, t_range=[0, 1])), run_time=0.45)
        crown = parts["crown"]
        self.play(crown.animate.scale(1.35), FadeOut(walker), run_time=0.2)
        self.play(crown.animate.scale(1 / 1.35), run_time=0.2)
        self.wait(0.3)
        self.play(FadeOut(parts["scene"]), FadeOut(parts["title"]), run_time=0.4)
        self.set_camera_orientation(**CAM_2D)  # nothing 3D on screen, so the switch is invisible

    # ------------------------------------------------------------ 1. data
    def data_step(self):
        head = self.fx(label(f"{len(LD['tickers16'])} ETFs · {LD['n_quarters']} quarters"))
        logp = np.array(LD["logp"])
        n, m = logp.shape
        w, h = 7.0, 3.6
        lo, hi = logp.min(), logp.max()
        cols = [LONG, COOL, QUANTUM, CUT, WARM, SHORT, GOOD, CLASSICAL]
        lines = VGroup()
        for i in range(n):
            pts = [np.array([-w / 2 + w * k / (m - 1), -1.6 + h * (logp[i, k] - lo) / (hi - lo), 0]) for k in range(m)]
            lines.add(VGroup().set_points_as_corners(pts).set_stroke(cols[i % len(cols)], 2.2, opacity=0.85))
        lines = VGroup(*[ln for ln in lines])
        cap1 = self.fx(T(f"daily prices, {LD['price_dates'][0][:4]}–{LD['price_dates'][1][:4]}", 32, MUTED)
                       .move_to(DOWN * 3.0))
        self.play(FadeIn(head), *self.set_progress(0), run_time=0.3)
        self.fx(lines)
        self.play(Create(lines, lag_ratio=0.02), FadeIn(cap1), run_time=0.9)
        grid = corr_grid(LD["corr16"], 4.6).move_to(DOWN * 0.1)
        cap2 = T("correlations, one quarter", 32, MUTED).move_to(DOWN * 3.0)
        self.fx(grid)
        grid.set_opacity(0)
        self.fx(cap2)
        cap2.set_opacity(0)
        self.play(FadeOut(lines), grid.animate.set_fill(opacity=1), FadeOut(cap1), cap2.animate.set_opacity(1),
                  run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(grid), FadeOut(cap2), FadeOut(head), run_time=0.3)

    # ------------------------------------------------------------ 2a. max-cut frustration
    def triangle_step(self):
        head = self.fx(label("Max-cut: can't cut every edge"))
        c = DOWN * 0.1
        tp = [c + UP * 1.7, c + LEFT * 2.0 + DOWN * 1.5, c + RIGHT * 2.0 + DOWN * 1.5]
        edges = [(0, 1, 3), (1, 2, 4), (0, 2, 5)]
        lines = VGroup(*[Line(tp[a], tp[b], color=MUTED, stroke_width=6) for a, b, _ in edges])
        wl = VGroup(*[weight_label(str(w), (tp[a] + tp[b]) / 2, 30) for a, b, w in edges])
        nodes = VGroup(*[Dot(p, radius=0.3, color=MUTED) for p in tp])
        self.fx(lines, nodes, wl)
        self.play(FadeIn(head), *self.set_progress(1), FadeIn(lines), FadeIn(nodes), FadeIn(wl), run_time=0.4)
        centre = sum(tp) / 3
        cut = None
        for deg in (100, 160):
            nrm = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg)), 0])
            sides = side_of(tp, centre, nrm)
            dvec = np.array([-nrm[1], nrm[0], 0])
            new = DashedLine(centre - 2.6 * dvec, centre + 2.6 * dvec, color=CUT, stroke_width=7)
            anims = [nd.animate.set_color(LONG if s > 0 else SHORT) for nd, s in zip(nodes, sides)]
            anims += [ln.animate.set_color(CUT if sides[a] != sides[b] else BAD) for ln, (a, b, _) in zip(lines, edges)]
            if cut is None:
                cut = self.fx(new)
                self.play(Create(cut), *anims, run_time=0.5)
            else:
                self.play(Transform(cut, new), *anims, run_time=0.5)
        uncut = self.fx(T("one edge always uncut", 36, BAD).move_to(DOWN * 3.1))
        self.play(FadeIn(uncut), run_time=0.3)
        self.wait(0.3)
        self.play(*[FadeOut(x) for x in (head, lines, nodes, wl, cut, uncut)], run_time=0.3)

    # ------------------------------------------------------------ 2b. the long-short book is a max-cut
    def book_step(self):
        head = self.fx(label("Long–short book = max-cut"))
        tick, corr, best = DATA["tickers"], np.array(DATA["corr"]), DATA["best_signs"]
        n = len(tick)
        c = DOWN * 0.2
        start = [c + 2.5 * np.array([np.cos(a), np.sin(a), 0])
                 for a in np.linspace(PI / 2, PI / 2 + 2 * PI, n, endpoint=False)]
        longs = [i for i in range(n) if best[i] > 0]
        shorts = [i for i in range(n) if best[i] < 0]
        target = list(start)
        for k, i in enumerate(longs):
            target[i] = np.array([-2.0, 2.0 - k * 1.3, 0]) + c
        for k, i in enumerate(shorts):
            target[i] = np.array([2.0, 2.0 - k * 1.3, 0]) + c
        dots = VGroup(*[Dot(p, radius=0.42, color=MUTED) for p in start])
        names = VGroup(*[T(t, 22, BG, "BOLD").move_to(p) for t, p in zip(tick, start)])
        for nm, d in zip(names, dots):
            nm.add_updater(lambda m_, d=d: m_.move_to(d.get_center()))
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if abs(corr[i, j]) >= 0.25]
        lines = VGroup()
        for i, j in pairs:
            v = corr[i, j]
            ln = Line(start[i], start[j], color=WARM if v > 0 else COOL, stroke_width=1.5 + 7 * abs(v),
                      stroke_opacity=0.3 + 0.5 * abs(v))
            ln.add_updater(lambda m_, i=i, j=j: m_.put_start_and_end_on(dots[i].get_center(), dots[j].get_center()))
            lines.add(ln)
        self.fx(lines, dots, names)
        self.play(FadeIn(head), *self.set_progress(1), FadeIn(lines), FadeIn(dots), FadeIn(names), run_time=0.5)
        self.wait(0.2)
        self.play(*[d.animate.move_to(p).set_color(LONG if best[i] > 0 else SHORT)
                    for i, (d, p) in enumerate(zip(dots, target))], run_time=0.7)
        cut = self.fx(DashedLine(UP * 2.5 + c, DOWN * 2.9 + c, color=CUT, stroke_width=7))
        tags = self.fx(VGroup(T("long", 34, LONG, "BOLD").move_to(np.array([-2.0, 2.85, 0]) + c),
                              T("short", 34, SHORT, "BOLD").move_to(np.array([2.0, 2.85, 0]) + c)))
        crossing = [k for k, (i, j) in enumerate(pairs) if best[i] != best[j] and corr[i, j] > 0]
        self.play(Create(cut), FadeIn(tags),
                  *[lines[k].animate.set_color(CUT).set_stroke(opacity=0.95) for k in crossing], run_time=0.5)
        cap = self.fx(fit(T("cut look-alikes apart = lower risk", 34, CUT), 7.4).move_to(DOWN * 3.75))
        self.play(FadeIn(cap), run_time=0.3)
        self.wait(0.5)
        for m_ in (*names, *lines):
            m_.clear_updaters()
        self.play(*[FadeOut(x) for x in (head, lines, dots, names, cut, tags, cap)], run_time=0.3)

    # ------------------------------------------------------------ 3. one peak vs many
    def landscape_step(self, L):
        lo = peak_surface(self.axes, L["long_only"])
        ls = peak_surface(self.axes, L["long_short"])
        h1 = self.fx(label(f"Long-only: {len(L['long_only'])} peak", 40, GOOD))
        self.play(FadeIn(h1), FadeIn(lo), *self.set_progress(2), run_time=0.5)
        self.wait(0.3)
        h2 = self.fx(label(f"Long–short: {len(L['long_short'])} peaks", 40, CUT))
        sub = self.fx(T("real local optima, one quarter", 30, MUTED).move_to(UP * 3.5))
        h2.set_opacity(0)
        sub.set_opacity(0)
        self.play(Transform(lo, ls), FadeOut(h1), h2.animate.set_opacity(1), sub.animate.set_opacity(1), run_time=0.9)
        self.wait(0.5)
        self.play(FadeOut(lo), FadeOut(h2), FadeOut(sub), run_time=0.3)

    # ------------------------------------------------------------ 4. the loop, quantum proposal
    def loop_step(self):
        head = self.fx(label("Same loop, quantum proposal"))

        def stage(y, title, color, glyph=None):
            box = RoundedRectangle(corner_radius=0.15, width=5.0, height=1.35, stroke_color=color, stroke_width=4,
                                   fill_color=color, fill_opacity=0.12).move_to(UP * y + LEFT * 0.4)
            txt = T(title, 36, color, "BOLD")
            if glyph is not None:
                inner = VGroup(glyph, txt).arrange(RIGHT, buff=0.3)
            else:
                inner = txt
            return VGroup(box, inner.move_to(box))

        def circuit_glyph():
            wires = VGroup(*[Line(LEFT * 0.55, RIGHT * 0.55, color=QUANTUM, stroke_width=3).shift(UP * (0.25 - 0.25 * k))
                             for k in range(3)])
            gates = VGroup(Rectangle(width=0.22, height=0.72, color=QUANTUM, fill_color=QUANTUM, fill_opacity=0.8,
                                     stroke_width=0).shift(LEFT * 0.28),
                           Rectangle(width=0.22, height=0.72, color=CUT, fill_color=CUT, fill_opacity=0.9,
                                     stroke_width=0),
                           Rectangle(width=0.22, height=0.72, color=QUANTUM, fill_color=QUANTUM, fill_opacity=0.8,
                                     stroke_width=0).shift(RIGHT * 0.28))
            return VGroup(wires, gates)

        cur = stage(2.0, "current book", FG)
        prop = stage(-0.1, "swap one holding", CLASSICAL)
        acc = stage(-2.2, "accept or reject", GOOD)
        a1 = Line(cur[0].get_bottom(), prop[0].get_top(), color=MUTED, stroke_width=4).add_tip(tip_length=0.2)
        a2 = Line(prop[0].get_bottom(), acc[0].get_top(), color=MUTED, stroke_width=4).add_tip(tip_length=0.2)
        back = CurvedArrow(acc[0].get_right() + RIGHT * 0.05, cur[0].get_right() + RIGHT * 0.05, angle=PI / 1.6,
                           color=MUTED, stroke_width=4)
        self.fx(cur, prop, acc, a1, a2, back)
        self.play(FadeIn(head), *self.set_progress(3),
                  LaggedStart(FadeIn(cur), FadeIn(a1), FadeIn(prop), FadeIn(a2), FadeIn(acc), FadeIn(back),
                              lag_ratio=0.15), run_time=0.7)
        self.wait(0.3)
        qprop = stage(-0.1, "quantum circuit", QUANTUM, circuit_glyph())
        self.fx(qprop)
        self.play(FadeOut(prop), FadeIn(qprop), run_time=0.5)
        self.wait(0.5)
        self.play(*[FadeOut(x) for x in (head, cur, qprop, acc, a1, a2, back)], run_time=0.3)

    # ------------------------------------------------------------ 5. where the move can go
    def move_bars(self, Q, row, dist, color, vmax, width=7.0, height=2.2):
        """One book's proposal distribution: a bar per book, grouped by swaps away, brighter = better book."""
        n = len(Q)
        groups = [[j for j in range(n) if dist[row][j] == d] for d in range(4)]
        gap = 0.35
        bw = (width - 3 * gap) / n
        bars, ticks = VGroup(), VGroup()
        x = -width / 2
        for d, g in enumerate(groups):
            x0 = x
            for j in sorted(g):  # books are in score order (worst first), so brighter = better
                h = max(height * np.sqrt(Q[row][j] / vmax), 0.03)
                col = interpolate_color(MUTED, color, 0.35 + 0.65 * j / (n - 1))
                bars.add(Rectangle(width=bw * 0.8, height=h, stroke_width=0, fill_color=col, fill_opacity=1)
                         .move_to(np.array([x + bw / 2, 0, 0]), aligned_edge=DOWN))
                x += bw
            ticks.add(T(str(d), 28, MUTED).move_to(np.array([(x0 + x) / 2, -0.3, 0])))
            x += gap
        base = Line(LEFT * width / 2, RIGHT * width / 2, color=MUTED, stroke_width=2)
        return VGroup(base, bars, ticks)

    def proposal_step(self):
        P = DATA["proposals"]
        longs = [set(b) for b in LD["book_longs"]]
        k = len(longs[0])
        dist = [[k - len(a & b) for b in longs] for a in longs]
        Qq, Qc = np.array(P["quantum"]), np.array(P["one_swap"])
        far = [Qq[r][np.array(dist[r]) >= 2].sum() for r in range(len(Qq))]
        row = int(np.argsort(far)[len(far) // 2])  # a typical book: median far-jump share
        vmax = max(Qc[row].max(), Qq[row].max())
        top = self.move_bars(Qc, row, dist, CLASSICAL, vmax).move_to(UP * 1.6)
        bot = self.move_bars(Qq, row, dist, QUANTUM, vmax).move_to(DOWN * 2.15)
        lt = T("Classical: next door", 38, CLASSICAL, "BOLD").move_to(UP * 3.4)
        lb = fit(T("Quantum: far, score-steered", 38, QUANTUM, "BOLD"), 7.4).move_to(DOWN * 0.1)
        tag = T("simulated", 24, MUTED).move_to(UP * 4.3)
        axis = T("swaps away from the current book", 26, MUTED).move_to(DOWN * 3.95)
        self.fx(top, lt, tag, axis)
        self.play(FadeIn(lt), FadeIn(tag), FadeIn(top[0]), FadeIn(top[2]), FadeIn(axis), *self.set_progress(3),
                  GrowFromEdge(top[1], DOWN), run_time=0.6)
        self.wait(0.3)
        self.fx(bot, lb)
        self.play(FadeIn(lb), FadeIn(bot[0]), FadeIn(bot[2]), GrowFromEdge(bot[1], DOWN), run_time=0.6)
        self.wait(1.0)
        self.play(*[FadeOut(x) for x in (top, bot, lt, lb, tag, axis)], run_time=0.3)

    # ------------------------------------------------------------ H. the real hardware run
    def hardware_step(self):
        chip = LD["chip"]
        head = self.fx(label("Ran on IBM quantum hardware", 38))
        sub = self.fx(T(f"{len(chip['used'])} qubits · {LD['hw_starts']} × {LD['hw_shots']:,} shots", 32, MUTED)
                      .move_to(UP * 3.5))
        pos = np.array(chip["positions"], float)
        s = min(6.4 / (pos[:, 0].max() - pos[:, 0].min()), 4.2 / (pos[:, 1].max() - pos[:, 1].min()))
        pts = [np.array([x * s, y * s, 0]) for x, y in pos]
        lat = VGroup(*[Line(pts[a], pts[b], color=MUTED, stroke_width=2, stroke_opacity=0.5) for a, b in chip["edges"]])
        qs = VGroup(*[Dot(p, radius=0.045, color=MUTED) for p in pts])
        board = VGroup(lat, qs).move_to(UP * 0.75)
        used = VGroup(*[Dot(qs[q].get_center(), radius=0.13, color=QUANTUM) for q in chip["used"]])
        name = T(chip["backend"], 24, MUTED).next_to(board, DOWN, buff=0.15)
        self.fx(board, name)
        self.play(FadeIn(head), FadeIn(sub), FadeIn(board), FadeIn(name), *self.set_progress(4), run_time=0.5)
        self.fx(used)
        self.play(LaggedStart(*[FadeIn(u, scale=2.5) for u in used], lag_ratio=0.12), run_time=0.5)
        # measured bitstrings (real counts, first starting book): green = valid book, red = noise
        strs = VGroup()
        for r in LD["stream"][:6]:
            t = T(r["bits"], 30, GOOD if r["valid"] else BAD, "BOLD")
            if not r["valid"]:
                t.set_opacity(0.5)
            strs.add(t)
        strs.arrange_in_grid(rows=2, buff=(0.45, 0.15)).move_to(DOWN * 3.3)
        self.fx(strs)
        src = used.get_center()
        self.play(LaggedStart(*[FadeIn(t, shift=(t.get_center() - src) * 0.25) for t in strs], lag_ratio=0.15),
                  run_time=0.8)
        valid = self.fx(T(f"{LD['hw_usable']:.0%} of shots valid", 26, GOOD).next_to(strs, UP, buff=0.15))
        self.play(FadeIn(valid), run_time=0.2)
        self.wait(0.5)
        self.play(*[FadeOut(x) for x in (head, sub, board, name, used, strs, valid)], run_time=0.3)

    # ------------------------------------------------------------ 6. result, then back to the hook
    def result_step(self):
        head = self.fx(label(f"Explores faster in {NUM['beats_multi_heldout']}\nof held-out quarters", 38, FG, y=4.05))
        tag = self.fx(fit(T("simulated · exact answers · tuned classical rivals", 26, MUTED), 7.4).move_to(UP * 3.25))
        bars_data = NUM["bars_etf_fair"]
        names = ["one swap", "multi-swap\n(tuned)", "quantum"]
        colors = [CLASSICAL, CLASSICAL, QUANTUM]
        base, hmax, vmax = -0.4, 2.6, 2.8
        bars = VGroup()
        for k, ((_, v), nm, col) in enumerate(zip(bars_data.items(), names, colors)):
            x = -2.4 + 2.4 * k
            rect = Rectangle(width=1.3, height=hmax * v / vmax, fill_color=col, fill_opacity=0.9, stroke_width=0)\
                .move_to(np.array([x, base, 0]), aligned_edge=DOWN)
            val = T(f"{v:.1f}×", 36, FG, "BOLD").next_to(rect, UP, buff=0.1)
            lab = T(nm, 26, MUTED).next_to(rect, DOWN, buff=0.12)
            bars.add(VGroup(rect, val, lab))
        speed = T("exploration speed", 26, MUTED).move_to(UP * 2.75)
        self.fx(bars, speed)
        self.play(FadeIn(head), FadeIn(tag), FadeIn(speed), *self.set_progress(5),
                  *[GrowFromEdge(b[0], DOWN) for b in bars], *[FadeIn(b[1:]) for b in bars], run_time=0.8)
        PQ = DATA["per_quarter"]
        grid = VGroup()
        labs = VGroup()
        cell = 0.29
        for u_i, uni in enumerate(("ETFs", "stocks")):
            vals = PQ[uni]["ratio"]
            half = (len(vals) + 1) // 2
            y0 = -2.55 - u_i * (2 * cell + 0.25)
            for c_i, v in enumerate(vals):
                r, cc = divmod(c_i, half)
                t = min(abs(np.log(v)) / np.log(2.5), 1.0)
                sq = Square(cell, stroke_width=1, stroke_color=BG, fill_color=GOOD if v > 1 else BAD,
                            fill_opacity=0.3 + 0.7 * t).move_to(np.array([-1.5 + cc * cell, y0 - r * cell, 0]))
                grid.add(sq)
            win = float(np.mean(np.array(vals) > 1))
            labs.add(VGroup(T(uni, 26, FG), T(f"{win:.0%}", 30, GOOD, "BOLD")).arrange(DOWN, buff=0.02)
                     .move_to(np.array([-2.6, y0 - cell / 2, 0])))
        self.fx(grid, labs)
        self.play(LaggedStart(*[FadeIn(s_) for s_ in grid], lag_ratio=0.01), FadeIn(labs), run_time=0.9)
        self.wait(0.9)
        # back to the opening frame so the loop is seamless
        parts = thumb.build()
        self.set_camera_orientation(**parts["camera"])  # nothing 3D on screen yet
        self.fx(parts["title"])
        self.play(*[FadeOut(x) for x in (head, tag, bars, speed, grid, labs, self.bar)],
                  FadeIn(parts["scene"]), FadeIn(parts["title"]), run_time=0.6)
