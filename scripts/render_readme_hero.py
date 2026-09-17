#!/usr/bin/env python3
"""Render the README hero film: assets/hero-concept-gate.gif (+ .mp4).

Story, one cut per stage of the skill:
  0 INTAKE        the brief
  1 CONCEPT GATE  three structurally different real previews, one chosen
  2 BUILD         the chosen direction built into a six-slide deck (real shots)
  3 VERIFY        projector + phone viewports, 0 errors
  4 END CARD      clear ideas before pixels

All footage is the skill's own output (example deck + verifier artifacts).
Field-manual palette/type, deterministic, Pillow + ffmpeg only.
"""
from __future__ import annotations

import math
import random
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "examples/previews"
SHOTS = ROOT / "examples/.preflight-check"
ASSETS = ROOT / "assets"

AVENIR = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"

PAPER = (244, 240, 230)
SHEET = (250, 247, 241)
INK = (26, 24, 21)
INK2 = (92, 85, 74)
INK3 = (150, 143, 128)
LINE = (202, 194, 178)
CINNABAR = (170, 48, 26)
CINNABAR_BRIGHT = (204, 63, 36)
CODE = (24, 22, 20)
CODE_PAPER = (232, 226, 214)
PINE = (47, 102, 74)

W, H = 1280, 720
FPS = 12

# (name, frame count)
SCENES = [("intake", 30), ("gate", 54), ("build", 48), ("verify", 46), ("end", 32)]


def font(path, size, index=0):
    return ImageFont.truetype(path, size=size, index=index)


F = {
    "h1": font(AVENIR, 60, 8),
    "h2": font(AVENIR, 34, 2),
    "brief": font(AVENIR, 31, 7),
    "brief_b": font(AVENIR, 31, 5),
    "mono": font(MENLO, 19, 0),
    "mono_b": font(MENLO, 19, 1),
    "mono_s": font(MENLO, 15, 0),
    "mono_xs": font(MENLO, 13, 0),
    "mono_xsb": font(MENLO, 13, 1),
    "term_l": font(MENLO, 22, 1),
}


def clamp(v):
    return max(0.0, min(1.0, v))


def ease_out(v):
    v = clamp(v)
    return 1 - (1 - v) ** 3


def ease_out_back(v):
    v = clamp(v)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (v - 1) ** 3 + c1 * (v - 1) ** 2


def tracked_w(d, text, fnt, tracking=0):
    return sum(d.textlength(ch, font=fnt) for ch in text) + tracking * max(0, len(text) - 1)


def tracked(d, xy, text, fnt, fill, tracking=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking


def center_tracked(d, cx, y, text, fnt, fill, tracking=0):
    tracked(d, (cx - tracked_w(d, text, fnt, tracking) / 2, y), text, fnt, fill, tracking)


def base(step_label):
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img)
    tracked(d, (64, 40), step_label, F["mono_xs"], CINNABAR, 3)
    tracked(d, (W - 64, 40), "MJORGIN/PREFLIGHT-DECKS", F["mono_xs"], INK3, 1)
    # right-align the top-right label
    d.rectangle((0, 0, 0, 0))
    d.line((64, 668, W - 64, 668), fill=LINE, width=1)
    return img, d


def stamp(text1, text2, scale=1.0, alpha=235):
    w, h = 300, 158
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    col = CINNABAR_BRIGHT + (alpha,)
    sd.rounded_rectangle((8, 8, w - 8, h - 8), radius=6, outline=col, width=4)
    sd.rounded_rectangle((17, 17, w - 17, h - 17), radius=4, outline=col, width=1)
    f1, f2 = font(MENLO, 26, 1), font(MENLO, 19, 1)
    sd.text(((w - tracked_w(sd, text1, f1, 2)) / 2, 40), text1, font=f1, fill=col)
    sd.text(((w - tracked_w(sd, text2, f2, 4)) / 2, 88), text2, font=f2, fill=col)
    rng = random.Random(412)
    px = layer.load()
    for _ in range(1500):
        x, y = rng.randrange(w), rng.randrange(h)
        r, g, b, a = px[x, y]
        if a:
            px[x, y] = (r, g, b, int(a * rng.uniform(0.55, 1.0)))
    layer = layer.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BICUBIC)
    return layer.rotate(-8, expand=True, resample=Image.BICUBIC)


def alpha_img(base_img, alpha):
    if alpha >= 255:
        return base_img
    out = base_img.copy()
    a = out.getchannel("A").point(lambda v: int(v * clamp(alpha / 255)))
    out.putalpha(a)
    return out


# ------------------------------------------------------------- scene 0

def scene_intake(f, n):
    img, d = base("STEP 0 — INTAKE")

    # Card
    card = (220, 150, 1060, 560)
    d.rounded_rectangle(card, radius=8, fill=SHEET, outline=LINE, width=2)
    tracked(d, (256, 188), "THE BRIEF", F["mono_xs"], CINNABAR, 3)

    lines = [
        ("“A pitch deck for our", F["brief"]),
        ("open-source presentation", F["brief"]),
        ("skill. It has to hold up", F["brief"]),
        ("on a projector — and a", F["brief"]),
        ("phone.”", F["brief"]),
    ]
    total_chars = sum(len(t) for t, _ in lines)
    shown_chars = int(clamp((f - 4) / 20) * total_chars)
    consumed = 0
    y = 250
    for text, fnt in lines:
        if shown_chars <= consumed:
            break
        n_chars = min(len(text), shown_chars - consumed)
        d.text((256, y), text[:n_chars], font=fnt, fill=INK)
        if n_chars == len(text) and f == 4 + 20 and False:
            pass
        consumed += len(text)
        y += 52

    if f >= 18:
        a = int(255 * ease_out((f - 18) / 5))
        warn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        wd = ImageDraw.Draw(warn)
        wd.rounded_rectangle((256, 500, 1024, 536), radius=4, fill=(170, 48, 26, a))
        wd.text((276, 507), "USUAL RESULT: NOTHING TO SAY · 3 RECOLORS · OVERFLOW ON STAGE",
                font=F["mono_xs"], fill=(PAPER[0], PAPER[1], PAPER[2], a))
        img.alpha_composite(warn)
    return img


# ------------------------------------------------------------- scene 1

THUMBS = [
    (PREVIEWS / "01-safe-swiss.png", "01", "SAFE PRESET"),
    (PREVIEWS / "02-bold-signal.png", "02", "BOLD TEMPLATE"),
    (PREVIEWS / "03-wildcard-manual.png", "03", "WILDCARD · FIELD MANUAL"),
]
TH_W, TH_H = 380, 214
TH_X0, TH_Y, TH_GAP = 40, 250, 30


def scene_gate(f, n):
    img, d = base("STEP 1 — CONCEPT GATE")
    center_tracked(d, W / 2, 110, "ONE BRIEF, THREE STRUCTURALLY DIFFERENT DIRECTIONS",
                   F["h2"], INK)

    chosen_start = 36
    for i, (path, idx, label) in enumerate(THUMBS):
        enter = ease_out((f - i * 8) / 8)
        if enter <= 0:
            continue
        x = TH_X0 + i * (TH_W + TH_GAP)
        y = TH_Y + int((1 - enter) * 26)
        slide = Image.open(path).convert("RGB").resize((TH_W, TH_H), Image.LANCZOS)
        chosen = i == 2
        dimmed = f >= chosen_start and not chosen
        frame = alpha_img(slide.convert("RGBA"), int(235 * enter))
        img.alpha_composite(frame, (x, y))
        if dimmed:
            wash = Image.new("RGBA", (TH_W, TH_H), PAPER + (168,))
            img.alpha_composite(wash, (x, y))
        bw = 3 if chosen and f >= chosen_start else 2
        col = CINNABAR_BRIGHT if chosen and f >= chosen_start else LINE
        d.rounded_rectangle((x - 2, y - 2, x + TH_W + 1, y + TH_H + 1),
                            radius=2, outline=col, width=bw)
        d.text((x, y - 34), idx, font=F["mono_b"], fill=CINNABAR if chosen else INK3)
        d.text((x + 44, y - 31), label, font=F["mono_s"],
               fill=CINNABAR if chosen else INK2)

    if f >= chosen_start:
        q = ease_out_back((f - chosen_start) / 8)
        a = int(240 * clamp((f - chosen_start) / 4))
        st = stamp("CHOSEN", "DIRECTION", scale=0.62 * q, alpha=a)
        img.alpha_composite(st, (TH_X0 + 2 * (TH_W + TH_GAP) + TH_W // 2 - st.width // 2,
                                 TH_Y + TH_H // 2 - st.height // 2))

    if f >= 40:
        a = int(255 * ease_out((f - 40) / 4))
        cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cap)
        cd.text((0, 0), "", font=F["mono"])
        txt = "you pick on pixels — then only the chosen direction gets built"
        tw = cd.textlength(txt, font=F["mono_s"])
        cd.rounded_rectangle((W / 2 - tw / 2 - 18, 526, W / 2 + tw / 2 + 18, 560),
                             radius=4, fill=(26, 24, 21, int(a * 0.9)))
        cd.text((W / 2 - tw / 2, 533), txt, font=F["mono_s"],
                fill=(PAPER[0], PAPER[1], PAPER[2], a))
        img.alpha_composite(cap)
    return img


# ------------------------------------------------------------- scene 2

BUILD_ORDER = [1, 2, 3, 4, 5, 6]
HOLD = 8


def scene_build(f, n):
    idx = min(f // HOLD, 5)
    local = f % HOLD
    num = BUILD_ORDER[idx]
    slide = Image.open(SHOTS / f"slide-{num:02d}-720p.png").convert("RGBA")
    a = int(255 * ease_out(local / 3))
    img = alpha_img(slide, a)
    d = ImageDraw.Draw(img)
    # paper caption chip
    chip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chip)
    cd.rounded_rectangle((40, 36, 330, 74), radius=4, fill=(244, 240, 230, 255))
    tracked(cd, (58, 47), f"BUILD  ·  {idx + 1:02d} / 06", F["mono_xsb"], CINNABAR, 2)
    img.alpha_composite(chip)
    return img


# ------------------------------------------------------------- scene 3

def scene_verify(f, n):
    img, d = base("STEP 2–3 — BUILD & VERIFY")
    d.text((64, 92), "Every slide is checked on the room it will actually meet.",
           font=F["h2"], fill=INK)

    # Projector shot
    proj_in = ease_out((f - 2) / 6)
    pj = Image.open(SHOTS / "slide-05-720p.png").convert("RGBA").resize((596, 335), Image.LANCZOS)
    pj = alpha_img(pj, int(255 * proj_in))
    px, py = 64, 170
    img.alpha_composite(pj, (px, py))
    d.rectangle((px - 2, py - 2, px + 597, py + 336), outline=INK, width=2)
    tracked(d, (px, py + 348), "1280 × 720  ·  PROJECTOR / 1080P", F["mono_xs"], INK2, 1)

    # Phone bezel
    ph_in = ease_out((f - 8) / 6)
    phone_src = Image.open(SHOTS / "slide-02-phone.png").convert("RGBA").resize((202, 436), Image.LANCZOS)
    phone_src = alpha_img(phone_src, int(255 * ph_in))
    hx, hy = 1002, 150
    d.rounded_rectangle((hx - 12, hy - 14, hx + 202 + 12, hy + 436 + 14),
                        radius=26, fill=INK)
    d.rounded_rectangle((hx - 4, hy - 6, hx + 206, hy + 442), radius=20, fill=(45, 42, 38))
    img.alpha_composite(phone_src, (hx, hy))
    tracked(d, (hx - 12, hy + 456), "390 × 844  ·  PHONE", F["mono_xs"], INK2, 1)

    # Terminal
    term_a = int(255 * ease_out((f - 14) / 6))
    term = Image.new("RGBA", (884, 150), CODE + (term_a,))
    td = ImageDraw.Draw(term)
    colp = CODE_PAPER + (term_a,)
    colc = CINNABAR_BRIGHT + (term_a,)
    td.text((22, 16), "$ python3 scripts/verify-deck.py pitch.html", font=F["mono_s"], fill=colp)
    if f >= 22:
        td.text((22, 50), "6 slides   ·   2 viewports   ·   0 overflow", font=F["mono_s"], fill=colp)
    if f >= 28:
        td.text((22, 86), "0 errors · 0 warnings", font=F["term_l"], fill=colc)
    img.alpha_composite(term, (64, 510))

    if f >= 32:
        q = ease_out_back((f - 32) / 8)
        st = stamp("CLEARED", "FOR LAUNCH", scale=0.5 * q, alpha=230)
        img.alpha_composite(st, (700 - st.width // 2, 585 - st.height // 2))
    return img


# ------------------------------------------------------------- scene 4

def scene_end(f, n):
    img, d = base("PREFLIGHT COMPLETE")
    a = ease_out(f / 8)
    center_tracked(d, W / 2, 200, "Clear ideas", F["h1"], INK, tracking=2)
    # cinnabar second line fades slightly after
    a2 = ease_out((f - 4) / 8)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    txt = "before pixels."
    tw = tracked_w(ld, txt, F["h1"], 2)
    tracked(ld, (W / 2 - tw / 2, 268), txt, F["h1"],
            CINNABAR + (int(255 * a2),), 2)
    img.alpha_composite(layer)

    if f >= 7:
        sub = "CONCEPT GATE · CRITIQUE LOOP · DUAL-VIEWPORT VERIFY"
        center_tracked(d, W / 2, 386, sub, F["mono_s"], INK2, 2)
    if f >= 10:
        url = "github.com/MJorgin/preflight-decks"
        uw = int(d.textlength(url, font=F["mono"])) + 48
        ux = int(W / 2 - uw / 2)
        d.rounded_rectangle((ux, 446, ux + uw, 496), radius=6, fill=CODE)
        d.text((ux + 24, 458), url, font=F["mono"], fill=CODE_PAPER)
    return img


SCENE_FN = {"intake": scene_intake, "gate": scene_gate, "build": scene_build,
            "verify": scene_verify, "end": scene_end}


def render_frame(global_f):
    acc = 0
    for name, count in SCENES:
        if global_f < acc + count:
            local = global_f - acc
            img = SCENE_FN[name](local, count)
            # global fade in/out
            if global_f < 6:
                img = alpha_img(img, int(255 * global_f / 6))
            total = sum(c for _, c in SCENES)
            if global_f > total - 7:
                img = alpha_img(img, int(255 * (total - global_f) / 6))
            return img.convert("RGB")
        acc += count
    raise IndexError(global_f)


def main():
    total = sum(c for _, c in SCENES)
    tmp = Path(tempfile.mkdtemp(prefix="pfd-hero-"))
    for i in range(total):
        render_frame(i).save(tmp / f"f{i:04d}.png")
    mp4 = ASSETS / "hero-concept-gate.mp4"
    gif = ASSETS / "hero-concept-gate.gif"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12.5",
                    "-i", str(tmp / "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    str(mp4)], check=True)
    palette = tmp / "pal.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                    "-vf", "fps=12.5,palettegen=stats_mode=diff", str(palette)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", palette,
                    "-lavfi", "fps=12.5,paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
                    str(gif)], check=True)
    print(f"frames {total}  duration {total / 12.5:.1f}s")
    for p in (mp4, gif):
        print(p, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
