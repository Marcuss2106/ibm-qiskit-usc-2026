"""Thumbnail: the real long-short landscape in 3D, with quantum jumps arcing between peaks.

Render one 1080x1350 portrait PNG (LinkedIn 4:5), from presentation/thumbnail/:
    manim -s -qh --format png thumbnail.py Thumbnail
The image lands in media/images/thumbnail/Thumbnail_ManimCE_v*.png.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    DEGREES, DL, DOWN, LEFT, OUT, UL, UP,
    Dot3D, ManimColor, ParametricFunction, Sphere, Surface, Text, ThreeDAxes, ThreeDScene,
    VGroup, config,
)

DATA = json.loads((Path(__file__).resolve().parent.parent / "data.json").read_text())
PEAKS = DATA["landscape3d"]["long_short"]  # 13 real local optima, one quarter, 16 ETFs, 8 vs 8

BG = ManimColor("#0b0d14")
FG = ManimColor("#e8ecf2")
MUTED = ManimColor("#8b94a5")
QUANTUM = ManimColor("#b57bff")
CLASSICAL = ManimColor("#9aa4b2")
COOL = ManimColor("#2bb3a3")
CUT = ManimColor("#f2c94c")
WARM = ManimColor("#e2574c")

config.background_color = BG
config.pixel_width, config.pixel_height = 1080, 1350  # portrait 4:5
config.frame_width, config.frame_height = 8.0, 10.0


def height(p):
    """Stretch the real scores (0.81 to 1.0) so the differences between peaks are visible."""
    return 0.25 + 1.75 * (p["h"] - 0.78) / 0.22


def f(u, v):
    z = 0.0
    for p in PEAKS:
        w = 0.09 + 0.30 * np.sqrt(p["share"])
        z = max(z, height(p) * np.exp(-((u - p["x"]) ** 2 + (v - p["y"]) ** 2) / (2 * w * w)))
    return z + 0.03 * np.sin(7 * u) * np.cos(6 * v)  # faint texture on the valley floor


def build():
    """Everything in the thumbnail: 3D parts, the fixed-in-frame title block, the camera, and the hop arcs.

    Shared with the LinkedIn loop (kept locally, not in the repo), whose opening frame is this thumbnail.
    """
    axes = ThreeDAxes(x_range=[-1.4, 1.4], y_range=[-1.4, 1.4], z_range=[0, 2.2],
                      x_length=6.2, y_length=6.2, z_length=2.9)
    surf = Surface(lambda u, v: axes.c2p(u, v, f(u, v)), u_range=[-1.35, 1.35], v_range=[-1.35, 1.35],
                   resolution=(72, 72), stroke_width=0.25, stroke_color=BG, fill_opacity=0.97)
    surf.set_fill_by_value(axes=axes, axis=2,
                           colorscale=[(ManimColor("#101826"), 0.0), (ManimColor("#17485a"), 0.35), (COOL, 0.8),
                                       (ManimColor("#6a4bc4"), 1.3), (CUT, 1.85), (WARM, 2.1)])

    def top(p, lift=0.06):
        return axes.c2p(p["x"], p["y"], f(p["x"], p["y"]) + lift)

    best = next(p for p in PEAKS if p["best"])
    stuck = PEAKS[0]  # a low peak: where small steps get trapped
    hops = [stuck, PEAKS[8], PEAKS[9], PEAKS[6], best]  # quantum route: far jumps, uphill each time

    # Classical walker: tiny steps circling its own small hill.
    rng = np.random.default_rng(3)
    walk = [np.array([stuck["x"], stuck["y"]])]
    for _ in range(26):
        walk.append(walk[-1] + rng.normal(0, 0.025, 2) - 0.25 * (walk[-1] - walk[0]))
    trail = VGroup(*[
        Dot3D(axes.c2p(x, y, f(x, y) + 0.03), radius=0.022, color=CLASSICAL).set_opacity(0.35 + 0.6 * i / len(walk))
        for i, (x, y) in enumerate(walk)
    ])
    classical = Sphere(top(stuck, 0.1), radius=0.11, resolution=(16, 16)).set_color(CLASSICAL)

    # Quantum jumps: glowing parabolic arcs from peak to peak.
    def arc(a, b, lift):
        pa, pb = np.array(top(a, 0.1)), np.array(top(b, 0.1))
        return lambda t: pa + (pb - pa) * t + OUT * lift * 4 * t * (1 - t)

    arcs = VGroup()
    paths = []
    for (a, b), lift in zip(zip(hops, hops[1:]), [0.8, 1.0, 1.2, 1.0]):
        path = arc(a, b, lift)
        paths.append(path)
        for width, opacity in [(26, 0.06), (16, 0.12), (9, 0.3), (3.5, 1.0)]:
            arcs.add(ParametricFunction(path, t_range=[0, 1], stroke_width=width,
                                        stroke_opacity=opacity, color=QUANTUM))
    landings = VGroup(*[Sphere(top(p, 0.1), radius=0.07, resolution=(12, 12)).set_color(QUANTUM)
                        for p in hops[1:-1]])

    # The best book: a bright marker with a halo.
    crown = VGroup(*[Sphere(top(best, 0.14), radius=r, resolution=(20, 20)).set_color(CUT).set_opacity(o)
                     for r, o in [(0.42, 0.08), (0.27, 0.18), (0.14, 1.0)]])

    camera = dict(phi=58 * DEGREES, theta=-100 * DEGREES, zoom=1.0,
                  frame_center=axes.c2p(0.0, 0.0, 0.6) + OUT * 1.6)

    title = Text("QeMCMC", font_size=72, weight="BOLD", color=FG)
    sub = Text("quantum-enhanced MCMC sampling", font_size=25, color=QUANTUM, weight="BOLD")
    line = Text("on real long–short ETF portfolios", font_size=22, color=MUTED)
    block = VGroup(title, sub, line).arrange(DOWN, buff=0.22)\
        .to_edge(UP, buff=0.7)
    return {"scene": VGroup(surf, trail, classical, arcs, landings, crown), "title": block, "camera": camera,
            "paths": paths, "crown": crown}


class Thumbnail(ThreeDScene):
    def construct(self):
        parts = build()
        self.set_camera_orientation(**parts["camera"])
        self.add(*parts["scene"])
        self.add_fixed_in_frame_mobjects(parts["title"])
