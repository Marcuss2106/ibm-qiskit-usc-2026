# Presentation (manim)

Five-minute talk, eight animated slides plus a backup. Script: `narration.md`.

## Setup (once)

manim needs Cairo and Pango development libraries (system packages):

```bash
sudo apt install -y libcairo2-dev libpango1.0-dev pkg-config ffmpeg
uv venv presentation/.venv --python 3.12
uv pip install --python presentation/.venv/bin/python "manim==0.21.0" numpy "manim-slides[pyside6]"
```

manim is pinned to 0.21.0: manim-slides 5.7.0 does not work with manim 0.22 (it sets the
removed `write_to_movie` config option).

`data.json` is committed; regenerate it from the project data with
`PYTHONPATH=. qiskit-env/bin/python presentation/make_data.py`.

## Render

```bash
cd presentation
.venv/bin/manim -pql slides.py FullTalk        # quick 480p preview of the whole talk
.venv/bin/manim -qh  slides.py FullTalk        # 1080p
.venv/bin/manim -pql slides.py Slide5Book      # one slide
```

## Slideshow (click to advance)

```bash
cd presentation
.venv/bin/manim-slides render --quality h slides.py FullTalkSlides   # note: --quality h, not -qh
.venv/bin/manim-slides present FullTalkSlides                         # presenter window
.venv/bin/manim-slides convert FullTalkSlides talk.html --one-file    # standalone HTML
```

In the presenter window: right arrow / space = next, left arrow = previous, F =
fullscreen, Q = quit. `talk.html` opens in any browser and needs no install (arrow keys,
F for fullscreen). `FullTalkSlides` pauses at each reveal across the eight slides, then shows the
backup slide for Q&A. Every `beat()` in `slides.py` is a timed
pause in the video and a click in the slideshow.

## Scenes

Scenes: `Slide1Title`, `Slide2Search`, `Slide3Hill`, `Slide4MaxCut`, `Slide5Book`,
`Slide6Quantum`, `Slide7Learned`, `Slide8Close`, `Backup`, `FullTalk` (all eight, timed video),
`FullTalkSlides` (slideshow, eight slides plus backup).
Output goes to `presentation/media/` (git-ignored).

Landscapes on slides 1, 3 and 8 and the max-cut graph on slide 4 are illustrative; the
correlation heat map, the long–short graph (edge weights = real correlations, final split =
the real optimal book from the hardware run) and all numbers are real.
