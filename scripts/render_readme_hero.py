#!/usr/bin/env python3
"""Render the README hero film: assets/hero-concept-gate.gif (+ .mp4).

Camera language follows docs/hero-film-storyboard.md: an establishing 1.06x
micro-push opens the film, one 1.3x push-in anchors on the chosen direction,
the verification wall drifts with 0.35/0.7/1.4 parallax layers, and the film
pulls back to a static full view before it ends. Every seam carries a
transition (defocus handoff, flash-wash, dip-to-dark); zoom durations come
from the log formula 0.55 * |ln(z2/z1)| / ln2.

Camera and HUD are separate layers: the camera moves only the world layer,
while step labels, the signature and the sheet rule stay fixed, the way
viewport chrome would in a real rig.

All footage is the skill's own output (example deck + verifier artifacts).
Deterministic, Pillow + ffmpeg only.

The verifier screenshots under `examples/.preflight-check/` are generated, not
committed, so this script bootstraps them: if they are missing it runs
`scripts/verify-deck.py` on the example deck first. A fresh clone therefore
rebuilds the film with one command (Playwright is already a requirement of the
skill).
"""
from __future__ import annotations

import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "examples/previews"
SHOTS = ROOT / "examples/.preflight-check"
ASSETS = ROOT / "assets"

SF = "/System/Library/Fonts/SFNS.ttf"
SFMONO = "/System/Library/Fonts/SFNSMono.ttf"

# Direction C · stage light. The names below are the roles the scenes use; the
# values are the dark stage so no scene code had to be rewritten to restyle it.
PAPER = (11, 12, 14)            # stage
SHEET = (24, 26, 31)            # panel
INK = (244, 245, 248)           # primary text
INK2 = (163, 168, 176)          # secondary
INK3 = (120, 126, 136)          # tertiary
LINE = (58, 62, 70)             # hairline
CINNABAR = (232, 72, 44)        # signal
CINNABAR_BRIGHT = (255, 94, 64)
AMBER = (226, 178, 120)         # eyebrow
CODE = (22, 24, 28)
CODE_PAPER = (226, 230, 236)

W, H = 1280, 720
FPS = 25

# World canvas bleeds past the stage so pans and zoomed framing never show
# the edge of the sheet (camera-language §3.3: bleed >= pan amplitude + 8%).
BX, BY = 180, 110
WORLD_W, WORLD_H = W + 2 * BX, H + 2 * BY

# (name, frames) — 496 frames total = 19.84s at 25fps
SCENES = [("intake", 90), ("gate", 115), ("build", 105), ("verify", 105), ("end", 81)]
# (cut frame, transition, half length in frames)
SEAMS = [(90, "defocus", 4), (205, "flash", 5), (310, "defocus", 4), (415, "dip", 7)]


def font(path, size, index=0):
    """Kept for the stamp helper; maps Menlo/SF Mono onto SF's variable axes."""
    f = ImageFont.truetype(path, size=size)
    try:
        f.set_variation_by_name("Bold" if index else "Regular")
    except Exception:
        pass
    return f


def sf(size, weight):
    f = ImageFont.truetype(SF, size=size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def mono(size, weight="Regular"):
    f = ImageFont.truetype(SFMONO, size=size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


F = {
    "h1": sf(60, "Bold"),
    "h2": sf(34, "Semibold"),
    "brief": sf(31, "Regular"),
    "mono": mono(19),
    "mono_b": mono(19, "Medium"),
    "mono_s": mono(15),
    "mono_xs": mono(13),
    "mono_xsb": mono(13, "Medium"),
    "term_l": mono(22, "Bold"),
}


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def ease_out(v):
    v = clamp(v)
    return 1 - (1 - v) ** 3


def ease_in_out(v):
    """power3.inOut — the easing camera-language §4.1 mandates for push/pull."""
    v = clamp(v)
    return 4 * v ** 3 if v < 0.5 else 1 - (-2 * v + 2) ** 3 / 2


def ease_out_back(v):
    v = clamp(v)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (v - 1) ** 3 + c1 * (v - 1) ** 2


def zoom_seconds(z_from, z_to):
    """camera-language §4.2 log duration formula, clamped to [0.30, 0.94]s."""
    d = 0.55 * abs(math.log(z_to / z_from)) / math.log(2)
    return clamp(d, 0.30, 0.94)


def tracked_w(d, text, fnt, tracking=0):
    return sum(d.textlength(ch, font=fnt) for ch in text) + tracking * max(0, len(text) - 1)


def tracked(d, xy, text, fnt, fill, tracking=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking


def center_tracked(d, cx, y, text, fnt, fill, tracking=0):
    tracked(d, (cx - tracked_w(d, text, fnt, tracking) / 2, y), text, fnt, fill, tracking)


def stage():
    """Stage-light background: black field, one soft wedge, film grain added later."""
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    wedge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wedge).polygon([(0, 0), (int(W * 0.72), 0), (int(W * 0.30), H), (0, H)],
                                  fill=(255, 252, 246, 22))
    img.alpha_composite(wedge.filter(ImageFilter.GaussianBlur(64)))
    glow = Image.radial_gradient("L").resize((int(W * 0.66), int(H * 0.72)), Image.LANCZOS)
    glow = glow.point(lambda v: max(0, 255 - v)).point(lambda v: int(v * 16 / 255))
    halo = Image.new("RGBA", glow.size, (255, 244, 226, 0))
    halo.putalpha(glow)
    img.alpha_composite(halo, (int(W * 0.04), int(H * 0.04)))
    return img, ImageDraw.Draw(img)


def hud(img, label, chip=False):
    """Fixed layer: step label, signature, sheet rule. Never moves with the camera."""
    d = ImageDraw.Draw(img)
    if chip:
        w = int(tracked_w(d, label, F["mono_xsb"], 3)) + 44
        d.rounded_rectangle((40, 34, 40 + w, 74), radius=4, fill=SHEET + (242,),
                            outline=(255, 255, 255, 34), width=2)
        tracked(d, (62, 46), label, F["mono_xsb"], AMBER, 3)
    else:
        d.rectangle((46, 46, 55, 55), fill=CINNABAR)
        tracked(d, (68, 44), label, F["mono_xsb"], AMBER, 3)
    sig = "MJORGIN/PREFLIGHT-DECKS"
    d.text((W - 64 - d.textlength(sig, font=F["mono_xs"]), 46), sig, font=F["mono_xs"], fill=INK3)
    d.line((64, 668, W - 64, 668), fill=LINE, width=1)
    return img


def stamp(text1, text2, scale=1.0, alpha=235):
    w, h = 300, 158
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    col = CINNABAR_BRIGHT + (alpha,)
    sd.rounded_rectangle((8, 8, w - 8, h - 8), radius=6, outline=col, width=4)
    sd.rounded_rectangle((17, 17, w - 17, h - 17), radius=4, outline=col, width=1)
    f1, f2 = font(SFMONO, 26, 1), font(SFMONO, 19, 1)
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


# --------------------------------------------------------------- camera rig

def apply_camera(sheet, zoom, cx, cy):
    """Crop a window out of the bled world and scale it to the output frame."""
    world = Image.new("RGB", (WORLD_W, WORLD_H), PAPER)
    world.paste(sheet.convert("RGB"), (BX, BY))
    win_w, win_h = W / zoom, H / zoom
    x = clamp(cx + BX - win_w / 2, 0, WORLD_W - win_w)
    y = clamp(cy + BY - win_h / 2, 0, WORLD_H - win_h)
    box = (int(round(x)), int(round(y)), int(round(x + win_w)), int(round(y + win_h)))
    return world.crop(box).resize((W, H), Image.LANCZOS)


TH_W, TH_H = 380, 214
TH_X0, TH_Y, TH_GAP = 40, 250, 30
THIRD_X = TH_X0 + 2 * (TH_W + TH_GAP) + TH_W / 2
THIRD_Y = TH_Y + TH_H / 2

CAM_PUSH_FRAMES = max(1, int(round(zoom_seconds(1.0, 1.3) * FPS)))     # 0.30s
CAM_PULL_FRAMES = max(1, int(round(zoom_seconds(1.15, 1.0) * FPS)))    # 0.30s


def cam_intake(f, n):
    # Establishing shot: start at 1.06x, ease back to full view over 3.0s.
    z = 1.06 - 0.06 * ease_in_out(f / (3.0 * FPS))
    return z, W / 2, H / 2


def cam_gate(f, n):
    # Apple's horizontal-rail language: pan across the three directions first,
    # then push in on the one that gets chosen.
    pan_end, push_start = 40, 44
    if f < push_start:
        return 1.0, W / 2 + 320 * ease_in_out(f / pan_end), H / 2
    t = ease_in_out((f - push_start) / CAM_PUSH_FRAMES)
    return (1.0 + 0.3 * t,
            (W / 2 + 320) + (THIRD_X - (W / 2 + 320)) * t,
            H / 2 + (THIRD_Y - H / 2) * t)


def cam_static(f, n):
    return 1.0, W / 2, H / 2


def cam_end(f, n):
    return 1.15 - 0.15 * ease_in_out(f / CAM_PULL_FRAMES), W / 2, H / 2


# -------------------------------------------------------------------- shots

def shot_intake(f, n):
    img, d = stage()
    d.rounded_rectangle((220, 150, 1060, 560), radius=8, fill=SHEET, outline=LINE, width=2)
    tracked(d, (256, 188), "THE BRIEF", F["mono_xs"], CINNABAR, 3)

    lines = [
        "“A pitch deck for our",
        "open-source presentation",
        "skill. It has to hold up",
        "on a projector — and a",
        "phone.”",
    ]
    total_chars = sum(len(t) for t in lines)
    shown = int(clamp((f - 4) / 78) * total_chars)
    consumed, y = 0, 250
    for text in lines:
        if shown <= consumed:
            break
        d.text((256, y), text[: min(len(text), shown - consumed)], font=F["brief"], fill=INK)
        consumed += len(text)
        y += 52

    if f >= 80:
        a = int(255 * ease_out((f - 80) / 6))
        warn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        wd = ImageDraw.Draw(warn)
        wd.rounded_rectangle((256, 500, 1024, 536), radius=4, fill=CINNABAR + (a,))
        wd.text((276, 507), "USUAL RESULT: NOTHING TO SAY · 3 RECOLORS · OVERFLOW ON STAGE",
                font=F["mono_xs"], fill=PAPER + (a,))
        img.alpha_composite(warn)
    return img


THUMBS = [
    (PREVIEWS / "01-safe-swiss.png", "01", "SAFE PRESET"),
    (PREVIEWS / "02-bold-signal.png", "02", "BOLD TEMPLATE"),
    (PREVIEWS / "03-wildcard-manual.png", "03", "WILDCARD · FIELD MANUAL"),
]
WASH_AT, STAMP_AT, CAPTION_AT = 30, 44, 52


def shot_gate(f, n):
    img, d = stage()
    center_tracked(d, W / 2, 110, "ONE BRIEF, THREE STRUCTURALLY DIFFERENT DIRECTIONS",
                   F["h2"], INK)

    for i, (path, idx, label) in enumerate(THUMBS):
        enter = ease_out((f - i * 8) / 8)
        if enter <= 0:
            continue
        x = TH_X0 + i * (TH_W + TH_GAP)
        y = TH_Y + int((1 - enter) * 26)
        frame = Image.open(path).convert("RGB").resize((TH_W, TH_H), Image.LANCZOS).convert("RGBA")
        if enter < 1:
            frame.putalpha(int(235 * enter))
        img.alpha_composite(frame, (x, y))
        if f >= WASH_AT and i < 2:
            img.alpha_composite(Image.new("RGBA", (TH_W, TH_H), PAPER + (168,)), (x, y))
        chosen = i == 2 and f >= WASH_AT
        d.rounded_rectangle((x - 2, y - 2, x + TH_W + 1, y + TH_H + 1), radius=2,
                            outline=CINNABAR_BRIGHT if chosen else LINE,
                            width=3 if chosen else 2)
        d.text((x, y - 34), idx, font=F["mono_b"], fill=CINNABAR if chosen else INK3)
        d.text((x + 44, y - 31), label, font=F["mono_s"], fill=CINNABAR if chosen else INK2)

    if f >= STAMP_AT:
        q = ease_out_back((f - STAMP_AT) / 8)
        a = int(240 * clamp((f - STAMP_AT) / 4))
        st = stamp("CHOSEN", "DIRECTION", scale=0.62 * q, alpha=a)
        img.alpha_composite(st, (int(THIRD_X - st.width / 2), int(THIRD_Y - st.height / 2)))

    if f >= CAPTION_AT:
        a = int(255 * ease_out((f - CAPTION_AT) / 5))
        cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cap)
        txt = "you pick on pixels — then only the chosen direction gets built"
        tw = cd.textlength(txt, font=F["mono_s"])
        cd.rounded_rectangle((W / 2 - tw / 2 - 18, 526, W / 2 + tw / 2 + 18, 560),
                             radius=4, fill=INK + (int(a * 0.9),))
        cd.text((W / 2 - tw / 2, 533), txt, font=F["mono_s"], fill=PAPER + (a,))
        img.alpha_composite(cap)
    return img


def shot_build(f, n):
    """The chosen direction becomes the deck: one continuous push, 52% -> 100%.

    The move is authored into the render rather than faked with a CSS scale —
    the film *is* the camera move (references/scroll-camera-recipes.md, #1).
    """
    t = ease_in_out((f / n - 0.18) / (0.72 - 0.18))
    w = int(W * (0.52 + 0.48 * t))
    slide = Image.open(SHOTS / "slide-01-720p.png").convert("RGB")
    h = int(w * slide.height / slide.width)
    x, y = (W - w) // 2, (H - h) // 2
    panel = slide.resize((w, h), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1),
                                           radius=max(6, int(w * 0.014)), fill=255)
    panel.putalpha(mask)
    img, d = stage()
    halo = Image.new("RGBA", (w + 240, h + 240), (0, 0, 0, 0))
    halo.paste(Image.new("RGBA", (w, h), (0, 0, 0, 205)), (120, 120), mask)
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(46)), (x - 120, y - 120))
    d.rounded_rectangle((x - 5, y - 5, x + w + 4, y + h + 4),
                        radius=int(max(8, w * 0.018)), outline=(255, 255, 255, 42), width=2)
    img.alpha_composite(panel, (x, y))
    return img


def shot_verify(f, n):
    img, d = stage()
    x = 32 * math.sin(math.pi * f / n)
    y = 10 * math.sin(2 * math.pi * f / n)

    # Far layer: headline, racking into focus over the first 12 frames.
    far = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(far).text((64, 92), "Every slide is checked on the room it will actually meet.",
                             font=F["h2"], fill=INK)
    if f < 12:
        far = far.filter(ImageFilter.GaussianBlur(3 * (1 - f / 12)))
    img.alpha_composite(far, (int(x * 0.35), int(y * 0.35)))

    # Mid layer: the two rooms.
    mid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mid)
    proj_in = ease_out((f - 2) / 6)
    if proj_in > 0:
        pj = Image.open(SHOTS / "slide-05-720p.png").convert("RGBA").resize((596, 335), Image.LANCZOS)
        pj.putalpha(int(255 * proj_in))
        mid.alpha_composite(pj, (64, 170))
        md.rectangle((62, 168, 662, 507), outline=INK, width=2)
        tracked(md, (64, 518), "1280 × 720  ·  PROJECTOR / 1080P", F["mono_xs"], INK2, 1)
    ph_in = ease_out((f - 8) / 6)
    if ph_in > 0:
        src = Image.open(SHOTS / "slide-02-phone.png").convert("RGBA").resize((202, 436), Image.LANCZOS)
        src.putalpha(int(255 * ph_in))
        hx, hy = 1002, 150
        md.rounded_rectangle((hx - 12, hy - 14, hx + 214, hy + 450), radius=26, fill=INK)
        md.rounded_rectangle((hx - 4, hy - 6, hx + 206, hy + 442), radius=20, fill=(45, 42, 38))
        mid.alpha_composite(src, (hx, hy))
        tracked(md, (hx - 12, hy + 456), "390 × 844  ·  PHONE", F["mono_xs"], INK2, 1)
    img.alpha_composite(mid, (int(x * 0.7), int(y * 0.7)))

    # Near layer: the receipt.
    near = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    term_a = int(255 * ease_out((f - 14) / 6))
    if term_a > 0:
        term = Image.new("RGBA", (884, 150), CODE + (term_a,))
        td = ImageDraw.Draw(term)
        colp, colc = CODE_PAPER + (term_a,), CINNABAR_BRIGHT + (term_a,)
        td.text((22, 16), "$ python3 scripts/verify-deck.py pitch.html", font=F["mono_s"], fill=colp)
        if f >= 22:
            td.text((22, 50), "6 slides   ·   2 viewports   ·   0 overflow", font=F["mono_s"], fill=colp)
        if f >= 28:
            td.text((22, 86), "0 errors · 0 warnings", font=F["term_l"], fill=colc)
        near.alpha_composite(term, (64, 510))
    if f >= 34:
        st = stamp("CLEARED", "FOR LAUNCH", scale=0.5 * ease_out_back((f - 34) / 8), alpha=230)
        near.alpha_composite(st, (700 - st.width // 2, 585 - st.height // 2))
    img.alpha_composite(near, (int(x * 1.4), int(y * 1.4)))
    return img


def shot_end(f, n):
    img, d = stage()
    center_tracked(d, W / 2, 200, "Clear ideas", F["h1"], INK, tracking=2)
    a2 = ease_out((f - 4) / 8)
    if a2 > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        txt = "before pixels."
        tw = tracked_w(ld, txt, F["h1"], 2)
        tracked(ld, (W / 2 - tw / 2, 268), txt, F["h1"], CINNABAR + (int(255 * a2),), 2)
        img.alpha_composite(layer)
    if f >= 7:
        center_tracked(d, W / 2, 386, "CONCEPT GATE · CRITIQUE LOOP · DUAL-VIEWPORT VERIFY",
                       F["mono_s"], INK2, 2)
    if f >= 10:
        url = "github.com/MJorgin/preflight-decks"
        uw = int(d.textlength(url, font=F["mono"])) + 48
        ux = int(W / 2 - uw / 2)
        d.rounded_rectangle((ux, 446, ux + uw, 496), radius=6, fill=CODE)
        d.text((ux + 24, 458), url, font=F["mono"], fill=CODE_PAPER)
    return img


SHOT_FN = {"intake": shot_intake, "gate": shot_gate, "build": shot_build,
           "verify": shot_verify, "end": shot_end}
CAM_FN = {"intake": cam_intake, "gate": cam_gate, "build": cam_static,
          "verify": cam_static, "end": cam_end}
LABELS = {"intake": "INTAKE", "gate": "CONCEPT GATE", "build": "BUILD",
          "verify": "VERIFY", "end": "PREFLIGHT COMPLETE"}


def scene_frame(index, local):
    name, _ = SCENES[index]
    sheet = SHOT_FN[name](max(0, local), SCENES[index][1])
    zoom, cx, cy = CAM_FN[name](max(0, local), SCENES[index][1])
    return hud(apply_camera(sheet, zoom, cx, cy), LABELS[name], chip=(name == "build"))


def ensure_verifier_shots():
    """The film is cut from the verifier's screenshots; generate them if absent.

    They are deliberately not committed (they are build output), so a fresh
    clone needs one verification run before the first render — this does it.
    """
    needed = ["slide-01-720p.png", "slide-02-phone.png", "slide-03-720p.png",
              "slide-04-720p.png", "slide-05-720p.png", "slide-06-720p.png"]
    if all((SHOTS / n).exists() for n in needed):
        return
    deck = ROOT / "examples" / "preflight-decks-pitch.html"
    print(f"verifier shots missing — running scripts/verify-deck.py {deck.relative_to(ROOT)}")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "verify-deck.py"), str(deck)],
                   check=True, cwd=ROOT)
    missing = [n for n in needed if not (SHOTS / n).exists()]
    if missing:
        raise SystemExit(
            "verify-deck.py ran but did not produce: " + ", ".join(missing) +
            "\nInstall the verifier deps first: python3 -m pip install playwright pillow"
            " && python3 -m playwright install chromium"
        )


def scene_start(index):
    return sum(n for _, n in SCENES[:index])


def scene_index_for(g):
    total = 0
    for i, (_, n) in enumerate(SCENES):
        if g < total + n:
            return i
        total += n
    return len(SCENES) - 1


def render_frame(g):
    for cut, kind, half in SEAMS:
        if not (cut - half <= g < cut + half):
            continue
        u = (g - cut) / half                      # -1 .. 1
        prev_i = scene_index_for(cut - 1)
        next_i = prev_i + 1
        if u < 0:
            prev_local = max(0, g - scene_start(prev_i))
            next_local = 0
        else:
            prev_local = SCENES[prev_i][1] - 1
            next_local = max(0, g - scene_start(next_i))
        a = ease_in_out((u + 1) / 2)
        prev, nxt = scene_frame(prev_i, prev_local), scene_frame(next_i, next_local)
        if kind == "defocus":
            r = 8 * (1 - abs(u))
            if r > 0.05:
                prev = prev.filter(ImageFilter.GaussianBlur(r))
                nxt = nxt.filter(ImageFilter.GaussianBlur(r))
        out = Image.blend(prev, nxt, a)
        if kind == "flash":
            out = Image.blend(out, Image.new("RGB", (W, H), (255, 253, 248)),
                              0.95 * (1 - abs(u)) ** 0.8)
        elif kind == "dip":
            out = Image.blend(out, Image.new("RGB", (W, H), (20, 20, 20)),
                              0.9 * (1 - abs(u)))
        return out
    return scene_frame(scene_index_for(g), g - scene_start(scene_index_for(g)))


def main():
    total = sum(n for _, n in SCENES)
    ensure_verifier_shots()
    tmp = Path(tempfile.mkdtemp(prefix="pfd-hero-"))
    for g in range(total):
        render_frame(g).save(tmp / f"f{g:04d}.png")

    mp4 = ASSETS / "hero-concept-gate.mp4"
    gif = ASSETS / "hero-concept-gate.gif"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(tmp / "f%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "19", str(mp4)], check=True)
    # Global palette + light ordered dither keeps the flat field-manual palette
    # crisp and the file near 2.5MB; the bayer scale is coarse so it does not
    # turn the paper texture into noise.
    palette = tmp / "pal.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                    "-vf", "fps=12.5,scale=960:540,palettegen=max_colors=48:stats_mode=single",
                    "-frames:v", "1", "-update", "1", str(palette)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", palette,
                    "-lavfi", "fps=12.5,scale=960:540,paletteuse=dither=none",
                    str(gif)], check=True)
    print(f"frames {total}  duration {total / FPS:.2f}s")
    for p in (mp4, gif):
        print(p.name, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
