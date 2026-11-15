# Presentation (manim)

Five-minute talk, seven animated slides plus a backup. Script: `narration.md`.

## Setup (once)

manim needs Cairo and Pango development libraries (system packages):

```bash
sudo apt install -y libcairo2-dev libpango1.0-dev pkg-config ffmpeg
uv venv presentation/.venv --python 3.12
uv pip install --python presentation/.venv/bin/python manim numpy
```

`data.json` is committed; regenerate it from the project data with
`PYTHONPATH=. qiskit-env/bin/python presentation/make_data.py`.

## Render

```bash
cd presentation
.venv/bin/manim -pql slides.py FullTalk        # quick 480p preview of the whole talk
.venv/bin/manim -qh  slides.py FullTalk        # 1080p
.venv/bin/manim -pql slides.py Slide5Morph     # one slide
```

Scenes: `Slide1Title`, `Slide2Search`, `Slide3Surprise`, `Slide4MaxCut`,
`Slide5Morph`, `Slide6Results`, `Slide7Takeaways`, `Backup`, `FullTalk` (all seven).
Output goes to `presentation/media/` (git-ignored).

Landscapes on slides 1, 3 and 7 are illustrative curves; the correlation heat map, the
long–short graph (edge = real correlation, final colouring = the real optimal book from
the hardware run) and all numbers are real.
