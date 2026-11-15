"""Dev helper: frames from rendered scenes -> one contact sheet per scene, plus durations.

    .venv/bin/python contact_sheets.py [quality_dir=480p15] [frames=8]
Writes media/sheets/<Scene>.png (git-ignored) and prints each scene's length.
"""
import sys
from pathlib import Path

import av
from PIL import Image, ImageDraw

QUALITY = sys.argv[1] if len(sys.argv) > 1 else "480p15"
FRAMES = int(sys.argv[2]) if len(sys.argv) > 2 else 8
SRC = Path(__file__).parent / "media" / "videos" / "slides" / QUALITY
OUT = Path(__file__).parent / "media" / "sheets"
OUT.mkdir(parents=True, exist_ok=True)

total = 0.0
for mp4 in sorted(SRC.glob("*.mp4")):
    with av.open(str(mp4)) as c:
        stream = c.streams.video[0]
        dur = float(stream.duration * stream.time_base)
        targets = [dur * (i + 0.5) / FRAMES for i in range(FRAMES)]
        frames, k = [], 0
        for frame in c.decode(stream):
            t = float(frame.pts * stream.time_base)
            if k < len(targets) and t >= targets[k]:
                img = frame.to_image()
                ImageDraw.Draw(img).text((8, 8), f"{t:5.1f}s", fill=(255, 255, 0))
                frames.append(img)
                k += 1
    if mp4.stem != "FullTalk":
        total += dur
    w, h = frames[0].size
    cols = 4
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows))
    for i, im in enumerate(frames):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(OUT / f"{mp4.stem}.png")
    print(f"{mp4.stem:18s} {dur:6.1f}s")
print(f"{'sum of slides':18s} {total:6.1f}s (includes Backup)")
