"""Shared cinematic-stage compositing for launch-page raster assets.

Used by render_site_previews.py and render_site_social_card.py so every
raster on the launch page speaks one lighting language: near-black gradient
plate, amber/cinnabar/cool ambient glows, floating rounded screens with
hairline bezels, floor shadow and reflection. Pure Pillow, deterministic.
"""
from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw, ImageFilter

CINNABAR = (232, 72, 44)
AMBER = (226, 178, 120)
COOL = (226, 238, 255)
INK = (236, 238, 244)
MUTE = (150, 156, 168)


def plate(w: int, h: int, *, top=(11, 14, 22), bottom=(4, 5, 9)) -> Image.Image:
    im = Image.new("RGBA", (w, h), top + (255,))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1)
        row = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line((0, y, w, y), fill=row + (255,))
    return im


def add_glow(base: Image.Image, color: tuple[int, int, int], fx: float, fy: float,
             fr: float, peak: float) -> None:
    w, h = base.size
    diameter = int(fr * 2 * w)
    glow = Image.new("RGBA", (diameter, diameter), color + (0,))
    mask = Image.new("L", (diameter, diameter), 0)
    md = ImageDraw.Draw(mask)
    for i in range(30, 0, -1):
        t = i / 30
        a = int(255 * peak * (1 - t) ** 1.5)
        r = diameter / 2 * t
        md.ellipse((diameter / 2 - r, diameter / 2 - r,
                    diameter / 2 + r, diameter / 2 + r), fill=a)
    mask = mask.filter(ImageFilter.GaussianBlur(diameter / 12))
    glow.putalpha(mask)
    base.alpha_composite(glow, (int(fx * w - diameter / 2),
                                int(fy * h - diameter / 2)))


def rounded_mask(w: int, h: int, radius: int) -> Image.Image:
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1),
                                           radius=radius, fill=255)
    return mask


def stage_screen(base: Image.Image, slide: Image.Image, x: int, y: int,
                 card_w: int, card_h: int, *, radius: int = 12,
                 chosen: bool = False, dark_slide: bool = False,
                 reflection: bool = True) -> None:
    """Composite a slide screenshot as a lit floating screen in place."""
    w, h = base.size

    if chosen:
        halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(halo).rounded_rectangle(
            (x - 8, y - 8, x + card_w + 8, y + card_h + 8),
            radius=radius + 8, fill=CINNABAR + (95,))
        base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(36)))

    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (x + 8, y + 34, x + card_w - 8, y + card_h + 58),
        radius=radius, fill=(0, 0, 0, 150))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(40)))

    card = slide.convert("RGBA").resize((card_w, card_h), Image.LANCZOS)
    card.putalpha(rounded_mask(card_w, card_h, radius))

    if reflection:
        refl_h = min(116, card_h // 5)
        refl = card.crop((0, card_h - refl_h, card_w, card_h)).transpose(
            Image.Transpose.FLIP_TOP_BOTTOM)
        fade = Image.new("L", (card_w, refl_h), 0)
        fp = fade.load()
        for yy in range(refl_h):
            a = int(255 * (1 - yy / refl_h) ** 1.6)
            for xx in range(card_w):
                fp[xx, yy] = a
        refl.putalpha(ImageChops.multiply(refl.getchannel("A"), fade))
        base.alpha_composite(refl, (x, y + card_h - 2))

    base.alpha_composite(card, (x, y))

    edge = ImageDraw.Draw(base)
    if chosen:
        outline, line_w = CINNABAR + (235,), 2
    else:
        outline, line_w = (255, 255, 255, 78 if dark_slide else 120), 1
    edge.rounded_rectangle((x, y, x + card_w - 1, y + card_h - 1),
                           radius=radius, outline=outline, width=line_w)
