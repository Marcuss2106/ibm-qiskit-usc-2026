# Presentation (manim)

Five-minute talk, nine animated slides plus a backup. Script: `narration.md`.

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
.venv/bin/manim-slides convert FullTalkSlides presentation.html          # HTML + presentation_assets/
```

In the presenter window: right arrow / space = next, left arrow = previous, F =
fullscreen, Q = quit. `presentation.html` (with its `presentation_assets/` folder) opens in any browser and needs no install (arrow keys,
F for fullscreen). `FullTalkSlides` pauses at each reveal across the nine slides, then shows the
backup slide for Q&A. Every `beat()` in `slides.py` is a timed
pause in the video and a click in the slideshow.

## Scenes

One scene per slide: `Slide1Title`, `Slide2Walk`, `Slide3Landscape`, `Slide4MaxCut`,
`Slide5Book`, `Slide6Move`, `Slide7Result`, `Slide8Limits`, `Slide9Contributions`, `Backup`;
`FullTalk` (all nine, timed video) and `FullTalkSlides` (slideshow, nine slides plus backup).
Output goes to `presentation/media/` (git-ignored).

The landscapes on slide 1 and the max-cut graphs on slide 4 are illustrative. The 3D
landscapes on slide 3 (real local optima of one quarter), the correlation graph and best
book on slide 5, the proposal tables on slide 6 (simulated, on the hardware-run instance)
and all numbers are real.

## LinkedIn loop (about 38 s, 4:5, silent)

`linkedin_gif.py` (`LinkedInLoop`): data → max-cut → landscape → move → hardware → result,
then back to the opening frame, which is the thumbnail (built by `thumbnail/thumbnail.py`'s `build()`). Reads `data.json` and `linkedin_data.json` (regenerate with
`PYTHONPATH=. qiskit-env/bin/python presentation/linkedin_data.py`). Everything shown is real
data except the toy triangle; the proposal bars are simulated, the chip and bitstrings are
from the ibm_marrakesh run.

```bash
cd presentation
# even pixel sizes only (an odd height segfaulted)
.venv/bin/manim render -qh --resolution=1080,1350 --fps 30 linkedin_gif.py LinkedInLoop
cp media/videos/linkedin_gif/1350p30/LinkedInLoop.mp4 linkedin_loop.mp4
ffmpeg -i linkedin_loop.mp4 -vf "fps=15,scale=720:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=diff" pal.png
ffmpeg -i linkedin_loop.mp4 -i pal.png -lavfi "fps=15,scale=720:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 linkedin_loop.gif
```
