#!/usr/bin/env python3
"""Render assets/demo-previews.png — the concept-gate comparison image.

The three source previews are 1280x720 landscape slides. A 3-up strip at
README width makes each slide unreadable, so this renders them as three
full-width labeled rows in the field-manual visual language.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo-previews.png"
SRCS = [
    (ROOT / "examples/previews/01-safe-swiss.png", "01",
     "SAFE PRESET", "competent, forgettable — the template default", False),
    (ROOT / "examples/previews/02-bold-signal.png", "02",
     "BOLD TEMPLATE", "louder and confident, but the same skeleton", False),
    (ROOT / "examples/previews/03-wildcard-manual.png", "03",
     "WILDCARD — LAUNCH PREFLIGHT FIELD MANUAL", "chosen, then built into the full deck", True),
]

AVENIR = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"

PAPER = (244, 240, 230)
INK = (26, 24, 21)
INK2 = (92, 85, 74)
INK3 = (150, 143, 128)
CINNABAR = (170, 48, 26)
LINE = (202, 194, 178)

W = 1600
PAD = 64
IMG_W = W - PAD * 2
IMG_H = IMG_W * 9 // 16
ROW_HEAD = 78
ROW_GAP = 40
TOP = 238
BOTTOM = 96


def font(path, size, index=0):
    return ImageFont.truetype(path, size=size, index=index)


def tracked(d, xy, text, fnt, fill, tracking=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking


def text_h(d, text, fnt):
    b = d.textbbox((0, 0), text, font=fnt)
    return b[3] - b[1]


def main():
    f_mono_xs = font(MENLO, 22)
    f_mono_s = font(MENLO, 26)
    f_mono_b = font(MENLO, 28)
    f_idx = font(MENLO, 40)
    f_h = font(AVENIR, 52, index=4)  # Avenir Next Medium, ttc index varies

    H = TOP + 3 * (ROW_HEAD + IMG_H + ROW_GAP) - ROW_GAP + BOTTOM
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    # Header
    tracked(d, (PAD, 56), "CONCEPT GATE", f_mono_xs, CINNABAR, 4)
    d.text((PAD, 92), "Same brief, three real directions.", font=f_h, fill=INK)
    d.text((PAD, 156), "Each is a structurally different slide — not one skeleton recolored",
           font=f_mono_s, fill=INK2)
    d.text((PAD, 192), "three times. You choose on pixels before a full deck exists.",
           font=f_mono_s, fill=INK2)

    y = TOP
    for src, idx, title, sub, chosen in SRCS:
        tracked(d, (PAD, y + 6), idx, f_idx, CINNABAR if chosen else INK3, 2)
        d.text((PAD + 110, y), title, font=f_mono_b, fill=INK)
        d.text((PAD + 110, y + 38), sub, font=f_mono_s, fill=INK2)

        slide = Image.open(src).convert("RGB").resize((IMG_W, IMG_H), Image.LANCZOS)
        sy = y + ROW_HEAD
        canvas.paste(slide, (PAD, sy))
        border_w = 4 if chosen else 2
        d.rectangle((PAD - border_w // 2, sy - border_w // 2,
                     PAD + IMG_W + border_w // 2 - 1, sy + IMG_H + border_w // 2 - 1),
                    outline=CINNABAR if chosen else LINE, width=border_w)

        if chosen:
            tag = "CHOSEN"
            tw = int(d.textlength(tag, font=f_mono_s)) + 34
            th = 42
            tx = PAD + IMG_W - tw - 24
            ty = sy + 24
            d.rectangle((tx, ty, tx + tw, ty + th), fill=CINNABAR)
            d.text((tx + 17, ty + 5), tag, font=f_mono_s, fill=PAPER)

        y += ROW_HEAD + IMG_H + ROW_GAP

    tracked(d, (PAD, H - 58), "ONLY THE CHOSEN DIRECTION IS BUILT INTO THE FULL DECK",
            f_mono_xs, INK3, 3)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT, optimize=True)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
