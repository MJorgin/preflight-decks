#!/usr/bin/env python3
"""Rebuild the launch-page hero filmstrip from the README master film.

The website hero is scroll-scrubbed from a tiled sprite (see
site/index.html). The source of truth is the full five-shot README film
assets/hero-concept-gate.mp4 (storyboard: docs/hero-film-storyboard.md);
this script samples FRAMES evenly across every shot, so the website can no
longer silently drift back to a two-clip recut.

Outputs (committed; CI never rebuilds them):
  site/assets/hero-filmstrip.webp   COLS x ROWS tiled sprite
  site/assets/hero_first.jpg        still shown before the sprite decodes
  site/assets/hero_last.jpg         sprite decode / no-canvas fallback

Requirements: ffmpeg on PATH, Pillow.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "hero-concept-gate.mp4"
SITE_ASSETS = ROOT / "site" / "assets"

FRAME_W, FRAME_H = 1280, 720
FRAMES = 72
COLS = 6
WEBP_QUALITY = 72
JPEG_QUALITY = 86


def ffprobe_frame_count() -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames", "-of",
         "csv=p=0", str(SOURCE)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return int(out)


def sample(total: int) -> list[int]:
    return [round(i * (total - 1) / (FRAMES - 1)) for i in range(FRAMES)]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing master film: {SOURCE}")
    total = ffprobe_frame_count()
    indices = sample(total)
    expression = "+".join(f"eq(n\\,{i})" for i in indices)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(SOURCE),
             "-vf", f"select='{expression}'", "-vsync", "0",
             str(tmp_path / "f%03d.png")],
            check=True,
        )
        frames = sorted(tmp_path.glob("f*.png"))
        if len(frames) != FRAMES:
            raise SystemExit(f"expected {FRAMES} frames, got {len(frames)}")
        images = [Image.open(f).convert("RGB") for f in frames]

        rows = (FRAMES + COLS - 1) // COLS
        strip = Image.new("RGB", (COLS * FRAME_W, rows * FRAME_H), (0, 0, 0))
        for i, im in enumerate(images):
            strip.paste(im, ((i % COLS) * FRAME_W, (i // COLS) * FRAME_H))
        strip.save(SITE_ASSETS / "hero-filmstrip.webp",
                   quality=WEBP_QUALITY, method=6)

        images[0].save(SITE_ASSETS / "hero_first.jpg",
                       quality=JPEG_QUALITY, optimize=True)
        images[-1].save(SITE_ASSETS / "hero_last.jpg",
                        quality=JPEG_QUALITY, optimize=True)

    print(f"wrote {FRAMES} sampled frames from {total} "
          f"({COLS}x{rows}) to site/assets/")


if __name__ == "__main__":
    main()
