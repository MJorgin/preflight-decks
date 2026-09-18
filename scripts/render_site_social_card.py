#!/usr/bin/env python3
"""Rebuild the 1280x640 OG/Twitter card on the launch-page stage.

The previous card was a light contact sheet that belonged to the old pale
site. This keeps the exact launch-page copy ("Clear ideas / before pixels.")
and shows the chosen direction floating on the same cinematic plate, so a
shared link already feels like the page behind it.

Source: assets/site-previews/dir-03.png (the chosen concept-gate direction).
Output: site/assets/social-card.png (idempotent overwrite).

Pure Pillow using macOS system SF Pro; run on macOS.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from sitestage import add_glow, AMBER, CINNABAR, COOL, INK, MUTE, plate, stage_screen

ROOT = Path(__file__).resolve().parents[1]
SF = "/System/Library/Fonts/SFNS.ttf"
SFMONO = "/System/Library/Fonts/SFNSMono.ttf"
W, H = 1280, 640


def sf(size: int, weight: str) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(SF, size=size)
    try:
        f.set_variation_by_name(weight)
    except OSError:
        pass
    return f


def tracked(draw: ImageDraw.ImageDraw, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main() -> None:
    base = plate(W, H)
    add_glow(base, AMBER, 0.10, -0.12, 0.46, 0.13)
    add_glow(base, CINNABAR, 0.92, -0.10, 0.5, 0.16)
    add_glow(base, COOL, 0.42, 1.18, 0.55, 0.09)

    # chosen direction as the floating screen (right two fifths)
    slide = Image.open(ROOT / "assets" / "site-previews" / "dir-03.png")
    card_w = 596
    card_h = round(card_w * 720 / 1280)
    stage_screen(base, slide, W - card_w - 84, (H - card_h) // 2 - 6,
                 card_w, card_h, chosen=True, reflection=False)

    d = ImageDraw.Draw(base)
    x = 84
    tracked(d, (x, 132), "PREFLIGHT DECKS", ImageFont.truetype(SFMONO, 18),
            AMBER + (255,), tracking=3)

    title = sf(74, "Bold")
    d.text((x - 3, 178), "Clear ideas", font=title, fill=INK + (255,))
    d.text((x - 3, 262), "before pixels.", font=title, fill=CINNABAR + (255,))

    sub = sf(25, "Regular")
    lines = wrap(d,
                 "Three directions, chosen on pixels — then verified on a "
                 "projector and a phone before delivery.", sub, 500)
    y = 372
    for line in lines:
        d.text((x, y), line, font=sub, fill=MUTE + (255,))
        y += 36

    base.convert("RGB").save(ROOT / "site" / "assets" / "social-card.png",
                             optimize=True)
    print("staged social-card.png")


if __name__ == "__main__":
    main()
