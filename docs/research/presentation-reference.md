# Presentation reference: Manim slides in the 3Blue1Brown style

A working reference for building our talk. It combines three things: how 3Blue1Brown
explains ideas, what the research on slides and speaking says, and how to build the
slides with Manim and `manim-slides`. Each claim is tagged with its source (list at the end).
Section 7 applies all of it to our QeMCMC long–short result.

**Confidence tags:** **[P]** primary source read (transcript, slides, source code, docs).
**[S]** secondary summary. Treat [S] items as sound advice, not exact quotes.

---

## 1. The ten rules (one-page version)

1. **One message per slide, stated as a full sentence.** The headline is the claim, and the
   picture below it is the evidence. [P: Doumont, Alley]
2. **Concrete before abstract.** Show an example first and the general framework after it.
   Definitions come last. [P: 3b1b FAQ]
3. **Open with a promise, not a joke or an outline.** In one sentence, say what the audience
   will know at the end that they don't know now. [P: Winston, Peyton Jones]
4. **Vision and evidence within the first 5 minutes,** or you have lost the room. [P: Winston]
5. **Every movement on screen has a purpose,** and it shows the same point the narration
   is making. [P: 3b1b FAQ]
6. **Few words on slides.** People have one language processor: they either read or listen.
   [P: Winston; S: Mayer redundancy]
7. **Narrow and deep beats wide and shallow.** Cover one key idea well and leave the rest to
   the paper or backup slides. [P: Peyton Jones]
8. **Cycle the main message three times** (opening, middle, end). At any moment, about 20% of
   the room is not listening. [P: Winston]
9. **Build a fence:** show what the idea is *not* (the nearest competitor, a near miss).
   [P: Winston]
10. **End on a contributions slide and a clear closing line, not "Thank you / Questions?"**
    [P: Winston]

---

## 2. How 3Blue1Brown structures an explanation

### 2.1 Grant Sanderson's stated principles

From his advice for SoME (Summer of Math Exposition), as listed in the 3b1b FAQ [P]:

| Principle | In his words | What it means for our slides |
|---|---|---|
| Concrete before abstract | "Give examples before general frameworks. Open with the key exercise; don't put it at the end." | Show one real window's landscape before defining "spectral gap". |
| Definitions last | "Topic definitions should not be seen as a starting point, but an ending point." "The best pedagogical order of ideas is often very different from the correct logical order." | Don't open with the Hamiltonian. Name it only after the audience has felt the need for it. |
| Be visual | "Always ask what picture or visual you could use to elucidate a topic." | Each slide needs one picture that carries the claim. |
| No pointless animation | "Every movement on the screen should be deliberate, with an identifiable purpose." Visuals and narration should "reinforce one another, rather than competing for the viewer's attention." | Animate only what changes conceptually. Never fly text in for decoration. |
| Know your genre | Student, expert, teacher and journalist "have different implications for pacing and style." | We are a student team presenting a result: honest, specific, no oversell. |
| Topic over polish | "Topic choice matters way more than production quality." | Get the story right before tuning animation curves. |

Other themes from interviews (secondary summaries) [S]:

- **Motivated explanation:** for each new idea, "is it clear where that idea came from?"
  Each definition should arrive once the problem it solves is clear.
- **Explanation as a path** "from the feeling of not understanding up to the feeling of
  understanding." Pose the question first, so the viewer *wants* the answer.
- **Leave room for the aha.** Let the audience almost guess the next step before you show it.
- **Story and characters:** recurring visual "characters" (the pi creatures, or a geometric
  object) that the audience follows through the video.

### 2.2 The typical 3b1b arc

This is a synthesis of the principles above and the shape of his videos, not a published
recipe:

1. **Hook:** a puzzle, surprising fact or concrete question. ("Why does π show up here?")
2. **Play with a specific case:** small numbers and one picture, worked out by hand.
3. **Notice the pattern:** the audience sees the structure before it has a name.
4. **Name and formalize:** now the definition or equation appears, built from pieces
   already on screen (equations *transform* out of earlier pictures, not from nowhere).
5. **Payoff:** answer the opening question with the new tool.
6. **Zoom out:** where it generalizes, and what it doesn't cover.

### 2.3 Visual grammar (from 3b1b's source code) [P]

- **Background:** black (`#000000`) in his video config. The ManimGL library default is dark
  grey `#333333`. Dark backgrounds make saturated colors pop. In a lit room with a weak
  projector, test both.
- **Fonts:** math in LaTeX Computer Modern. Text in **CMU Serif** (the Computer Modern
  text face), centered. This makes words and math look like one family.
- **Consistent color coding:** each variable keeps the same color in every equation and
  scene. His example scenes pass one shared `t2c` (tex-to-color) map to every equation.
- **Palette (ManimGL hex values):**

| Role (our suggestion) | Constant | Hex |
|---|---|---|
| Primary object / quantum proposal | BLUE_C | `#58C4DD` |
| Secondary / classical baseline | GREY_B | `#BBBBBB` |
| Highlight / "look here" | YELLOW_D | `#F4D345` |
| Good outcome | GREEN_C | `#83C167` |
| Bad outcome / cost | RED_C | `#FC6255` |
| Second quantity | TEAL_C | `#5CD0B3` |
| Third quantity | GOLD_C | `#F0AC5F` |
| De-emphasized / background | GREY_D | `#444444` |

  Manim Community's constants differ slightly (e.g. CE `YELLOW` is `#F7D96F`, ManimGL
  `yellow_c` is `#FFFF00`). Pick one set and define it once in a shared `style.py`.
  Note: red/green alone is not colorblind-safe. Pair the color with shape or position, or
  use blue vs. orange for the main contrast.

- **Animation vocabulary he uses** (from `example_scenes.py`): `Write` for text and
  equations; `ShowCreation` (CE: `Create`) for curves and graphs; `TransformMatchingStrings`
  (CE: `TransformMatchingTex`) to morph one equation into the next; `TransformFromCopy` to
  derive a new thing from an old one while the original stays; `FadeIn(x, UP)` /
  `FadeOut(x, shift=DOWN)` with a direction; `LaggedStart` for groups; `Indicate` and
  `FlashAround` to point at a sub-expression. **Highlight sub-terms instead of using a
  laser pointer.**

---

## 3. What the research on slides says

### 3.1 Assertion–evidence slides (Alley) [P]

- Replace the default topic-phrase headline plus bullets with a **sentence headline** (one or
  two lines, left-aligned) stating the takeaway, supported by **visual evidence** (graph,
  diagram, photo, animation). No bullet lists.
- Evidence: in Garner, Alley et al. (IJEE 2013), two audiences heard the same talk with
  different slides. The assertion–evidence group understood and remembered more, with fewer
  misconceptions and lower perceived cognitive load. A second study found that *presenters*
  who built assertion–evidence slides understood their own material better.
- Counterpoint (Farkas 2010): sentence headlines can tempt speakers to read them aloud, and
  not every slide has a natural visual. Fix: **don't read the headline**. Say it in
  different words, or let the animation land first and then say it.

| Bad (topic) | Good (assertion) |
|---|---|
| "Results" | "The quantum proposal mixes faster in 81–91% of held-out windows" |
| "Landscape analysis" | "Long-only portfolios have one peak; long–short books have many" |
| "Hardware" | "On today's hardware, the cheap circuit mixes slower than a classical swap" |

### 3.2 Multimedia learning (Mayer) [S]

The principles with the strongest support for live slides:

- **Coherence:** remove anything that doesn't serve the message (logos, backgrounds,
  decorative animation). This is one of Mayer's largest effects.
- **Signaling:** cue what matters (highlight, color, arrow, `Indicate`).
- **Redundancy:** don't show on screen the same sentences you are saying. Words on screen
  should be labels, not paragraphs.
- **Segmenting:** break the explanation into audience-paced chunks. In `manim-slides`, each
  `next_slide()` is a segment.
- **Pre-training:** introduce key terms and parts *before* the main explanation (e.g. "a book
  is a long/short split" before showing the landscape).
- **Spatial and temporal contiguity:** put labels next to what they label, and narrate while
  the animation happens, not after it.

### 3.3 Doumont, *Trees, Maps, and Theorems* [P]

- Three laws: **adapt to your audience; maximize signal-to-noise; use effective
  redundancy.**
- **"With each slide, convey one message (only). State the message verbally, then develop it
  visually."**
- Slides should "make sense on their own", so they are redundant with what you say.
- Structure: attention getter → need → task → **main message (the one sentence they
  should remember)** → preview (ideally 3 points, at most 5) → points with transitions →
  review → conclusion → close.
- Questions: listen to the whole question, repeat or rephrase it, give a brief answer to the
  whole room. Under attack, acknowledge the concern first.

### 3.4 Peyton Jones, "How to give a great research talk" [P]

- The goal is "to give your audience an intuitive feel for your idea" and to make them want
  to read the paper, not to show everything you know. **Paper = the beef, talk = the
  advertisement.**
- Plan for about **20% motivation, 80% key idea.** You have about **2 minutes** before people
  doze: why should I listen, what is the problem, why is it interesting?
- **Identify a key idea.** Say "If you remember nothing else, remember this."
  Ruthlessly prune anything that doesn't serve it.
- **"Examples are your main weapon."** "When time is short, omit the general case, not the
  example."
- **No outline slide at the start** (it conveys nearly nothing). Orient *after* the
  motivation and use signposts at pause points.
- Omit dense technical notation and refer to the paper. Keep backup slides for questions.
- Don't reveal bullet points one by one "unless there is a punch line". Use animation
  effects "very very … sparingly". (Manim animation should *explain*, not reveal.)
- Show enthusiasm, don't apologize, face the audience, **finish on time**.

---

## 4. Talk structure and delivery (Winston, Duarte)

### 4.1 Patrick Winston, "How to Speak" (MIT) [P]

**Opening**
- No joke at the start ("they're not ready for a joke"). Use an **empowerment promise**:
  "tell people what they're going to know at the end … that they didn't know at the
  beginning."

**Four heuristics**
- **Cycle:** go round the idea three times, because about 20% of listeners are "fogged out"
  at any moment.
- **Build a fence:** distinguish your idea from similar ones ("his is exponential, mine's
  linear").
- **Verbal punctuation:** number and announce the seams ("the third idea is …") so people
  can "get back on the bus."
- **Ask a question:** you can wait about **7 seconds** for an answer. Make it neither too
  obvious nor too hard.

**Slides**
- "There are always too many slides, always too many words." Slides should be "condiments",
  not the main event.
- Remove background junk, logos and unnecessary titles. Text at roughly **40 pt minimum**;
  35 pt is a sign you are cramming.
- **No laser pointers** (you turn your back and lose the room). **Put an arrow on the slide**
  instead. In Manim: `Arrow`, `Indicate`, `SurroundingRectangle`.
- Print the deck and lay it on a table to check whether it is "too heavy" (not enough air or
  imagery).
- You may use **one** deliberately overwhelming slide per talk (a "hapax legomenon"), for
  example the full 2^n landscape.

**Persuading (job or research talk)**
- Within **5 minutes**, show **vision** (a problem someone cares about plus something new
  in your approach) and that **you've done something** (the steps to the solution).
- **Situate** the work: who else is working on this, and why it matters.
- Rehearse with people who *don't* know your work. Insiders "hallucinate" missing material.

**Being remembered: Winston's star (five S's)**
- **Symbol** (a picture people associate with the work), **Slogan** (a handle phrase),
  **Surprise**, **Salient idea** (one that sticks out, not merely important), **Story**.

**Ending**
- The last slide is **Contributions** (what *you* did), not Conclusions, not a collaborator
  list (credit them on the first slide), not "Questions?" and not "Thank you". It stays up
  during Q&A.
- Final words: a closing joke is fine at the *end*, or a **salute** to the audience. "Thank
  you" as the last words is "a weak move."

### 4.2 Duarte's sparkline (Resonate) [S]

Great talks alternate between **"what is"** (the current reality) and **"what could be"**
(the better future), and end on a **"new bliss"** plus a call to action. Use it for
pacing: each problem → result → limitation → next step cycle is one swing. Note that our
honest limitations ("simulation only", "hardware is slower") are legitimate "what is"
beats, not things to hide.

### 4.3 Delivery checklist (Winston, Peyton Jones, Doumont)

- **Script the first few sentences exactly** (nerves peak there). Memorize the *outline*,
  not the wording, for everything else.
- Face the audience, not the screen. Have the laptop in front of you, showing speaker notes.
- Speak to the back row. Find a "nodder" and talk to them.
- Cut filler words and **value silence**. Pause after each key result before advancing.
- Pace: as a rule of thumb (ours, not from a source), about 1 slide per minute with
  `manim-slides` sub-steps inside slides. A 10-minute talk ≈ 8–12 slides.
- Encourage questions. If time runs short, cut material rather than run over: "Absolutely
  without fail, finish on time."
- Never ask "would you like me to go on?" and never apologize ("I didn't have time to …").
- Test the projector and resolution beforehand. Bring an offline HTML/PDF export on USB.

---

## 5. Building it with Manim + manim-slides

### 5.1 Setup [P: manim-slides docs]

```bash
pip install -U "manim-slides[manim,pyside6-full]"    # inside a venv; Qt needed for `present` since v5.1
manim-slides render talk.py Talk                     # wraps `manim render`
manim-slides present Talk                            # fullscreen: -F ; start paused: --start-paused
manim-slides convert Talk talk.html --one-file       # RevealJS export, press S for speaker view
manim-slides convert Talk talk.pdf                   # static fallback (last frame of each slide)
manim-slides convert Talk talk.pptx                  # PowerPoint with embedded videos
```

Manim also needs LaTeX (installed here) and ffmpeg (installed here). Use `-ql` while
iterating and `-qh` / `-qk` for the final render.

### 5.2 `Slide.next_slide` parameters [P]

`next_slide(loop=False, auto_next=False, playback_rate=1.0, reversed_playback_rate=1.0,
notes='', dedent_notes=True, skip_animations=False, src=None, direction='horizontal')`

- `loop=True`: the slide loops until you press next. Good for "the chain is still running"
  idle states. (In HTML export, a loop can't be the first or last slide.)
- `notes="..."`: speaker notes in Markdown. They show in `present`, the HTML speaker view and
  pptx.
- `auto_next=True`: chain into the next slide with no keypress (present/HTML only).
- `skip_animations=True` or `start_skip_animations()` / `stop_skip_animations()`: skip
  rendering finished sections while iterating on a later one.
- `src=Path(...)`: drop in a pre-rendered video as a slide.
- Helpers: `self.wipe(old, new, direction=LEFT)` slides old content out and new content in.
  `self.zoom(old, new)` does a zoom transition. `self.add_to_canvas(title=...)` keeps
  persistent items (slide counter, footer). Then use
  `self.wipe(self.mobjects_without_canvas, new)` to swap the body only.

### 5.3 Shared style module (pattern)

```python
# slides/style.py — one place for all visual decisions
from manim import *

BG      = "#000000"
QUANTUM = "#58C4DD"   # BLUE_C
CLASSIC = "#BBBBBB"   # GREY_B
FOCUS   = "#F4D345"   # YELLOW_D
GOOD    = "#83C167"   # GREEN_C
BAD     = "#FC6255"   # RED_C
DIM     = "#444444"   # GREY_D

# Every equation in the deck uses this map, so symbols keep their color everywhere.
T2C = {r"\mu": TEAL_C, r"\Sigma": GOLD_C, r"\lambda": FOCUS, "x": QUANTUM}

config.background_color = BG
Text.set_default(font="CMU Serif")          # install the CMU fonts, or fall back to a clean sans

def headline(s: str) -> Text:
    """Assertion headline: one sentence, top-left, at most two lines."""
    return Text(s, font_size=34).to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.5)
```

### 5.4 Scene skeleton (pattern; untested here, since Manim isn't installed in this env)

```python
from manim import *
from manim_slides import Slide
from style import *

class Landscape(Slide):
    def construct(self):
        # 1. Assertion headline first: the message, as a sentence.
        h = headline("Long–short books have many local optima; long-only has one")
        self.play(FadeIn(h, shift=DOWN * 0.2))
        self.next_slide(notes="Say it in other words, don't read it.")

        # 2. Concrete before abstract: one real window, no notation yet.
        bars = ...  # e.g. BarChart of scores for a handful of books
        self.play(Create(bars))
        self.next_slide()

        # 3. Signal, don't point: highlight on screen instead of a laser.
        self.play(Indicate(bars[0], color=FOCUS))
        self.next_slide()

        # 4. Only now, the formula, colored with the shared T2C map.
        eq = MathTex(r"S(x) = ", r"\mu^\top x", r" - \lambda\, x^\top \Sigma x",
                     tex_to_color_map=T2C).next_to(h, DOWN, buff=0.6)
        self.play(Write(eq))
        self.next_slide()

        # 5. Equations evolve, never cut: morph into the long–short version.
        eq2 = MathTex(...)  # long–short score, same T2C
        self.play(TransformMatchingTex(eq, eq2))
        self.next_slide()

        # 6. Clear the stage between ideas.
        self.wipe(self.mobjects_without_canvas, [])
```

### 5.5 Animation do / don't

| Do | Don't |
|---|---|
| `TransformMatchingTex` / `TransformFromCopy` so new equations grow out of old ones | Fade one equation out and an unrelated one in |
| `Indicate`, `Circumscribe`, `SurroundingRectangle`, `Arrow` to direct attention | Laser pointer; moving text around for "energy" |
| `LaggedStart` for a group (cards, bars) so the eye can follow | Animate 20 objects at once, or one by one with long waits |
| Dim what is no longer relevant (`set_opacity(0.3)`, `DIM` color) | Leave everything on screen and keep adding |
| Keep a moving object in the same place across slides (visual continuity) | Re-layout the same diagram differently each slide |
| `run_time` of about 1–2 s per idea; `self.wait()` is free in slides (you control the pace) | Long auto-play sequences that outrun your narration |
| Load real plots as `ImageMobject` or render data with `Axes`/`BarChart` | Screenshot tables full of numbers |

---

## 6. Slide anatomy checklist

For every slide:

- [ ] Headline is a **full-sentence claim**, at most 2 lines.
- [ ] One message. If the headline needs "and", split the slide.
- [ ] One visual carries the evidence. No bullets (or at most 3 short labels).
- [ ] Text ≥ about 28 px equivalent at 1080p; no paragraph text.
- [ ] Colors follow the shared map; the same thing has the same color everywhere.
- [ ] Every animation has a purpose you can name.
- [ ] Speaker notes hold the narration (`notes=`), not the slide.
- [ ] Nothing on the slide that you won't talk about (coherence).

For the deck:

- [ ] Opens with a promise, not an outline or a joke.
- [ ] Problem + "we did something" both land within 5 minutes.
- [ ] Main message appears three times (open, middle, close).
- [ ] At least one "fence": what this result is *not* (e.g. "not faster optimization").
- [ ] Ends on Contributions, then a closing line or salute (not "Thank you / Questions?").
- [ ] Backup slides for likely questions (hardware details, gate counts, baselines).
- [ ] Rehearsed out loud at least twice with someone outside the project, and timed.
- [ ] Offline HTML/PDF export on a USB stick.

---

## 7. Applied: outline for our QeMCMC talk (5 minutes)

The numbers come from `research_results.md`. Headlines are assertions. The plan is 7 slides
in about 4:20, which leaves about 40 s of slack for nerves, a slow transition or a demo
hiccup. In a 5-minute talk, Winston's "vision plus evidence in 5 minutes" shrinks to about
**90 seconds**: the audience should know the problem and that we have a result by the end
of slide 3.

| # | Time | Assertion headline (draft) | Visual (Manim) | Say |
|---|---|---|---|---|
| 1 | 0:25 | "Where does a quantum proposal actually beat classical moves?" | Title, team names (credits here); a walker hopping between portfolios | Promise: by the end you'll know where it wins *and* where it doesn't |
| 2 | 0:35 | "Picking a portfolio is a walk, and bad moves get stuck on local peaks" | Books as bit strings with swap edges, then a 1-D landscape with a ball stuck on a peak | MCMC in one sentence; the proposal move is what we're changing |
| 3 | 0:45 | "Long-only portfolios have one peak; long–short books have many" | Landscape morphs from 1 peak (all 64 windows) to rugged (median 13 optima) | Surprise: the famous problem is too easy. Rugged landscapes are where moves matter |
| 4 | 0:40 | "Our move: a count-preserving XY mixer plus a score phase" | Circuit builds up: mix → score phase → mix | Keeps the long/short count fixed; the phase uses the score to steer proposals |
| 5 | 0:55 | "It mixes faster than tuned classical moves in 81–91% of held-out windows" | Gap-ratio distribution, line at 1 highlighted; sub-step: the phase-off version falls back below 1 | **Main message.** The control shows the score phase is the source of the gain |
| 6 | 0:35 | "But it's a sampling win, simulated, and too deep for today's hardware" | Three small tiles: ✓ sampling / ✗ finding the best book / ✗ ~540 two-qubit gates (hardware run slower) | State the limits plainly; it protects the claim |
| 7 | 0:25 | Contributions (stays up for Q&A) | 3 lines: found where the landscape is rugged; quantum proposal mixes faster there; identified the phase as the cause | Restate the slogan, then a one-line salute. No "Thank you / Questions?" |

**Cut from the 10-minute version** (move to backup slides for Q&A): the separate
bit-string example, the 64-window long-only chart, the side-by-side phase-off slide, and
the ibm_marrakesh hardware details. Each is now a sub-step or a tile instead of its own
slide.

**If you're running long, drop in this order:** the bit-string half of slide 2, then
slide 4's circuit build (show the finished circuit at once), then the tiles on slide 6
(say it in one sentence over slide 5).

**Script these word for word:** the opening sentence (slide 1), the main message (slide 5)
and the last sentence (slide 7). Memorize only the outline for everything else.

Winston's star for this talk (draft):
- **Symbol:** the rugged landscape morphing from one peak to many.
- **Slogan:** "Rugged problems, quantum moves."
- **Surprise:** the famous problem (long-only) is too easy; the gain only appears on a
  rugged landscape.
- **Salient idea:** the score phase is what does the work (phase-off control).
- **Story:** how we went from "quantum loses everywhere" to finding where it wins.

---

## 8. Sources

Primary (read in full or in part):
- Sanderson, G. 3Blue1Brown FAQ, "I'd like to start making math videos…" (points from the
  SoME1 announcement). https://www.3blue1brown.com/faq/
- 3b1b source: https://github.com/3b1b/manim/blob/master/manimlib/default_config.yml ,
  https://github.com/3b1b/manim/blob/master/example_scenes.py ,
  https://github.com/3b1b/videos/blob/master/custom_config.yml
- Winston, P. "How to Speak", MIT OCW RES.TLL-005 (2018), transcript.
  https://ocw.mit.edu/courses/res-tll-005-how-to-speak-january-iap-2018/
- Peyton Jones, S. "How to give a great research talk" (slides, 2016 update).
  https://www.microsoft.com/en-us/research/academic-program/give-great-research-talk/
- Doumont, J.-l. *Trees, Maps, and Theorems* (Principiae, 2009), "Effective oral
  presentations" summary sheet. https://www.principiae.be/
- Alley, M. Assertion–evidence approach. https://www.assertion-evidence.com/ ; research list
  https://writing.engr.psu.edu/research.html
- Garner, J. K., Alley, M., Wolfe, K., Sawarynski, L. (2013). Assertion-evidence slides appear
  to lead to better comprehension and recall of more complex concepts. *Int. J. Engineering
  Education* 29(6). https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf
- manim-slides docs (API, CLI, quickstart). https://manim-slides.eertmans.be/latest/ ;
  https://github.com/jeertmans/manim-slides
- Manim Community docs v0.22. https://docs.manim.community/en/stable/

Secondary (summaries; wording not verified against the original):
- Buteau, A. "Lessons from Grant Sanderson". https://www.antoinebuteau.com/lessons-from-grant-sanderson/
- Dwarkesh Patel interview with Grant Sanderson. https://www.dwarkesh.com/p/grant-sanderson
- Sanderson on motivated explanations (summary of his 2026 guest post on Terence Tao's blog).
  https://ai-tldr.dev/releases/grant-sanderson-motivated-explanations/
- Mayer, R. E., multimedia principles: Chartered College summary https://my.chartered.college/?p=6958 ;
  Mayer 2020 handout https://ugc.futurelearn.com/uploads/files/7d/d6/7dd6188d-c343-4311-b064-ac98d2c95abc/Multimedia_Principles._R._E._Mayer__2020.pdf
- Farkas, D. (2010), critique of Alley's slide design.
  https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf
- Duarte, N. *Resonate* (2010) and "The secret structure of great talks" (TEDx).
  https://www.duarte.com/resources/secret-structure-great-talks/

Not obtained: a transcript of the SoME1 advice video and the Nicky Case comic summarizing it.
