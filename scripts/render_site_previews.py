#!/usr/bin/env python3
"""Stage raw slide screenshots for the launch page.

The rail + pinned screenshots used to be raw slide exports dropped straight
into a dark page: near-blank white canvases and one dark red blob, three
different worlds. The previews now keep every slide pixel intact (a preview
must stay the real slide) but float as lit screens on the cinematic plate
shared with the hero — see sitestage.py.

Source slides (committed, provenance = the concept-gate + built deck):
  assets/site-previews/{dir-01,dir-02,dir-03,deck-05}.png
Outputs (overwritten every run, idempotent):
  site/assets/{dir-01,dir-02,dir-03,deck-05}.png

Pure Pillow, deterministic, no network. Run: python3 scripts/render_site_previews.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from sitestage import add_glow, AMBER, CINNABAR, COOL, plate, stage_screen

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "assets" / "site-previews"
OUT_DIR = ROOT / "site" / "assets"
W, H = 1280, 720

CARD_W = 1056
CARD_H = round(CARD_W * 720 / 1280)  # 594
CARD_X = (W - CARD_W) // 2
CARD_Y = 66

JOBS = [
    ("dir-01.png", {"chosen": False, "dark_slide": False}),
    ("dir-02.png", {"chosen": False, "dark_slide": True}),
    ("dir-03.png", {"chosen": True, "dark_slide": False}),
    ("deck-05.png", {"chosen": False, "dark_slide": False}),
]


def build(slide: Image.Image, *, chosen: bool, dark_slide: bool) -> Image.Image:
    base = plate(W, H)
    add_glow(base, AMBER, 0.16, 0.0, 0.42, 0.12)
    add_glow(base, CINNABAR, 0.92, -0.08, 0.46, 0.24 if chosen else 0.12)
    add_glow(base, COOL, 0.5, 1.14, 0.52, 0.10)
    stage_screen(base, slide, CARD_X, CARD_Y, CARD_W, CARD_H,
                 chosen=chosen, dark_slide=dark_slide)
    return base.convert("RGB")


def main() -> None:
    for name, flags in JOBS:
        slide = Image.open(SRC_DIR / name)
        build(slide, **flags).save(OUT_DIR / name, optimize=True)
        print("staged", name)


if __name__ == "__main__":
    main()
