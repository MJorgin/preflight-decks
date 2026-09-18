#!/usr/bin/env python3
"""Render the README concept-gate contact sheet on the cinematic stage."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from sitestage import add_glow, AMBER, CINNABAR, COOL, INK, MUTE, plate, stage_screen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo-previews.png"

SF = "/System/Library/Fonts/SFNS.ttf"
SFMONO = "/System/Library/Fonts/SFNSMono.ttf"

W = 1600
TOP = 250
CARD_X, CARD_W, CARD_H = 240, 1120, 630
PITCH = 730
H = TOP + 3 * PITCH + 135

ROWS = [
    ("01", "01-safe-swiss.png", ("SAFE", "PRESET"),
     "Competent, but template-default", False),
    ("02", "02-bold-signal.png", ("BOLD", "TEMPLATE"),
     "Louder, but the same skeleton", False),
    ("03", "03-wildcard-manual.png", ("WILDCARD", "FIELD MANUAL"),
     "Chosen, then built into the full deck", True),
]


def sf(size, weight="Regular"):
    font = ImageFont.truetype(SF, size=size)
    try:
        font.set_variation_by_name(weight)
    except OSError:
        pass
    return font


def mono(size, weight="Regular"):
    font = ImageFont.truetype(SFMONO, size=size)
    try:
        font.set_variation_by_name(weight)
    except OSError:
        pass
    return font


def tracked(draw, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    base = plate(W, H)
    add_glow(base, AMBER, 0.14, -0.02, 0.48, 0.11)
    add_glow(base, CINNABAR, 0.92, -0.08, 0.52, 0.14)
    add_glow(base, COOL, 0.48, 1.08, 0.54, 0.08)
    d = ImageDraw.Draw(base)

    tracked(d, (240, 70), "CONCEPT GATE", mono(22, "Medium"), AMBER + (255,), 4)
    d.text((236, 112), "Same brief, three real directions.",
           font=sf(66, "Bold"), fill=INK + (255,))
    d.text((240, 196), "Each is structurally different — not one skeleton recolored three times.",
           font=sf(27), fill=MUTE + (255,))

    f_index, f_title, f_note = mono(44, "Medium"), mono(20, "Medium"), sf(22)
    for i, (idx, filename, title_lines, note, chosen) in enumerate(ROWS):
        y = TOP + i * PITCH
        slide = Image.open(ROOT / "examples" / "previews" / filename)
        stage_screen(base, slide, CARD_X, y, CARD_W, CARD_H,
                     radius=16, chosen=chosen, dark_slide=i == 1)

        color = CINNABAR if chosen else (150, 156, 168)
        d.text((72, y + 205), idx, font=f_index, fill=color + (255,))
        for j, line in enumerate(title_lines):
            tracked(d, (72, y + 278 + j * 30), line, f_title, INK + (255,), 2)
        for j, line in enumerate(wrap(d, note, f_note, 142)):
            d.text((72, y + 352 + j * 30), line, font=f_note, fill=MUTE + (255,))

        if chosen:
            x1 = 72
            d.rounded_rectangle((x1, y + 24, x1 + 164, y + 62), radius=19,
                                fill=CINNABAR + (238,))
            tracked(d, (x1 + 21, y + 36), "CHOSEN DIRECTION", mono(15, "Medium"),
                    (255, 255, 255, 255), 1)

    tracked(d, (240, H - 72), "ONLY THE CHOSEN DIRECTION IS BUILT INTO THE FULL DECK",
            mono(18, "Medium"), (150, 156, 168, 255), 3)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(OUT, optimize=True)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
