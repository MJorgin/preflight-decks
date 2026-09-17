#!/usr/bin/env python3
"""Mechanical verification for fixed-stage HTML decks.

Screenshots every slide at 1280x720 and the first slides at 390x844, then
checks the 16:9 fixed-stage contract: uniform scaling, no overflow, no blank
slides, no placeholder leftovers. Writes screenshots, a contact sheet (when
Pillow is available), and report.json into <deck>/.preflight-check/.

Usage:
    python3 verify-deck.py deck.html [--out DIR] [--slides-selector SEL]
                                     [--stage-selector SEL] [--limit N]

Exit codes: 0 all checks passed (warnings allowed); 1 tooling/config error;
2 one or more hard verification errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(
    r"lorem ipsum|placeholder text|\btodo\b|\btbd\b|\bxxx+\b|"
    r"占位|示例文字|待补充|请在此",
    re.IGNORECASE,
)
GENERIC_FONT_RE = re.compile(
    r"font-family\s*:[^;}]*(inter|roboto|arial|system-ui|helvetica)",
    re.IGNORECASE,
)

# Evaluated in the page. Returns the index of the currently shown slide.
JS_ACTIVE_INDEX = r"""
(sel) => {
  const nodes = [...document.querySelectorAll(sel)];
  let best = -1, bestArea = 0;
  nodes.forEach((el, i) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity < 0.1) return;
    if (r.width < 50 || r.height < 50) return;
    const area = r.width * r.height;
    if (area > bestArea) { bestArea = area; best = i; }
  });
  return best;
}
"""

JS_SLIDE_STATE = r"""
(args) => {
  const [sel, stageSel] = args;
  const nodes = [...document.querySelectorAll(sel)];
  const idx = nodes.findIndex(n => n === document.activeElement);
  const active = (() => {
    let best = -1, bestArea = 0;
    nodes.forEach((el, i) => {
      const s = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity < 0.1) return;
      if (r.width < 50 || r.height < 50) return;
      const area = r.width * r.height;
      if (area > bestArea) { bestArea = area; best = i; }
    });
    return best;
  })();
  const el = nodes[active];
  if (!el) return {active, errors: ['no visible slide']};
  const errors = [];
  if (el.scrollWidth > el.clientWidth + 1)
    errors.push(`overflow-x ${el.scrollWidth - el.clientWidth}px`);
  if (el.scrollHeight > el.clientHeight + 1)
    errors.push(`overflow-y ${el.scrollHeight - el.clientHeight}px`);

  // Descendants poking outside the slide box.
  const r = el.getBoundingClientRect();
  const vw = window.innerWidth, vh = window.innerHeight;
  let escapes = 0;
  el.querySelectorAll('*').forEach(c => {
    const cr = c.getBoundingClientRect();
    const cs = getComputedStyle(c);
    if (cr.width === 0 && cr.height === 0) return;
    if (cs.position === 'fixed') return;
    if (cr.left < r.left - 1 || cr.top < r.top - 1 ||
        cr.right > r.right + 1 || cr.bottom > r.bottom + 1) {
      // ignore scaled-stage bleed that stays inside the viewport margin
      if (cr.left < -1 || cr.top < -1 || cr.right > vw + 1 || cr.bottom > vh + 1) escapes++;
    }
  });
  if (escapes) errors.push(`elements outside slide/viewport: ${escapes}`);

  const text = (el.textContent || '').trim();
  const visibleEls = el.querySelectorAll('*').length;
  const blank = text.length < 2 && visibleEls < 3;

  // Stage geometry: pick the selector candidate closest to 16:9, then a
  // class-matched ancestor, then the parent. Avoids wrapper elements
  // (flex viewports) whose box matches the viewport rather than the stage.
  const boxOf = node => {
    if (!node) return null;
    const b = node.getBoundingClientRect();
    if (b.width < 50 || b.height < 50) return null;
    return {node, w: b.width, h: b.height, ratio: b.width / b.height};
  };
  let stageBox = null;
  const direct = [...document.querySelectorAll(stageSel)].map(boxOf).filter(Boolean);
  if (direct.length) {
    stageBox = direct.reduce((a, b) =>
      Math.abs(b.ratio - 16 / 9) < Math.abs(a.ratio - 16 / 9) ? b : a);
  }
  if (!stageBox) {
    const anc = el.closest('[class*="stage"],[class*="deck"]');
    const pb = boxOf(anc) || boxOf(el.parentElement);
    if (pb) stageBox = pb;
  }
  let geo = null;
  if (stageBox) {
    geo = {w: Math.round(stageBox.w), h: Math.round(stageBox.h),
           ratio: +stageBox.ratio.toFixed(4),
           fits: stageBox.w <= vw + 1 && stageBox.h <= vh + 1,
           pageScrollX: document.documentElement.scrollWidth - vw,
           pageScrollY: document.documentElement.scrollHeight - vh};
  }
  return {active, errors, blank, textLen: text.length, visibleEls, geo};
}
"""


def load_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa
        return sync_playwright
    except ImportError:
        sys.exit(
            "Playwright is required: python3 -m pip install playwright && "
            "python3 -m playwright install chromium"
        )


def make_contact_sheet(out_dir: Path, shots: list[Path], columns: int = 2) -> Path | None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    images = [Image.open(p) for p in shots]
    tw, th = 480, 270
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tw, rows * (th + 22)), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(images):
        im = im.resize((tw, th))
        x, y = (i % columns) * tw, (i // columns) * (th + 22)
        sheet.paste(im, (x, y + 22))
        d.text((x + 8, y + 4), shots[i].stem, fill=(230, 230, 230))
    path = out_dir / "contact-sheet.png"
    sheet.save(path)
    return path


def verify(html: Path, out_dir: Path, slides_sel: str, stage_sel: str, limit: int | None):
    sync_playwright = load_playwright()
    source = html.read_text(encoding="utf-", errors="replace")

    warnings, hard_errors = [], []
    if PLACEHOLDER_RE.search(source):
        for m in set(PLACEHOLDER_RE.findall(source)):
            warnings.append(f"placeholder text in source: {m!r}")
    if GENERIC_FONT_RE.search(source):
        warnings.append("generic font leads a font-family stack (Inter/Roboto/Arial/system-ui)")

    results = []
    shots720, shots_phone = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page.goto(html.resolve().as_uri())
        page.wait_for_timeout(700)

        count = page.evaluate("(sel) => document.querySelectorAll(sel).length", slides_sel)
        if not count:
            sys.exit(f"No slides matched {slides_sel!r}; pass --slides-selector")
        total = min(count, limit) if limit else count

        seen = set()
        for _ in range(total + 2):
            state = page.evaluate(JS_SLIDE_STATE, [slides_sel, stage_sel])
            i = state["active"]
            if i < 0 or i in seen:
                before = i
                page.keyboard.press("ArrowRight")
                page.wait_for_timeout(260)
                state = page.evaluate(JS_SLIDE_STATE, [slides_sel, stage_sel])
                i = state["active"]
                if i == before or i < 0:
                    page.keyboard.press("Space")
                    page.wait_for_timeout(260)
                    state = page.evaluate(JS_SLIDE_STATE, [slides_sel, stage_sel])
                    i = state["active"]
            if i < 0 or i in seen:
                break
            seen.add(i)

            shot = out_dir / f"slide-{i + 1:02d}-720p.png"
            page.screenshot(path=shot)
            shots720.append(shot)

            geo = state.get("geo") or {}
            errs = list(state["errors"])
            if geo.get("pageScrollX", 0) > 1 or geo.get("pageScrollY", 0) > 1:
                errs.append(f"page scrolls (x={geo['pageScrollX']}, y={geo['pageScrollY']})")
            if geo and not geo.get("fits", True):
                errs.append("stage larger than 1280x720 viewport")
            if state.get("blank"):
                errs.append("blank slide (no text, almost no elements)")

            results.append({"slide": i + 1, "viewport": "1280x720",
                            "errors": errs, "geometry": geo,
                            "text_len": state.get("textLen"),
                            "visible_elements": state.get("visibleEls")})
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(260)

        missing = [i + 1 for i in range(total) if i not in seen]
        if missing:
            hard_errors.append(f"could not navigate to slides {missing} via keyboard")

        # Phone viewport: fixed stage must scale whole, stay 16:9, fit.
        phone = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        phone.goto(html.resolve().as_uri())
        phone.wait_for_timeout(700)
        for target in range(min(3, total)):
            for _ in range(target + 1):
                phone.keyboard.press("ArrowRight")
                phone.wait_for_timeout(200)
            state = phone.evaluate(JS_SLIDE_STATE, [slides_sel, stage_sel])
            shot = out_dir / f"slide-{target + 1:02d}-phone.png"
            phone.screenshot(path=shot)
            shots_phone.append(shot)
            geo = state.get("geo") or {}
            errs = list(state["errors"])
            ratio = geo.get("ratio")
            if ratio and abs(ratio - 16 / 9) > 0.03:
                errs.append(f"phone stage ratio {ratio} != 16:9 (content reflowed?)")
            if geo and not geo.get("fits", True):
                errs.append("stage does not fit 390x844 viewport")
            if geo.get("pageScrollX", 0) > 1:
                errs.append("horizontal page scroll on phone")
            results.append({"slide": target + 1, "viewport": "390x844",
                            "errors": errs, "geometry": geo})
        browser.close()

    for r in results:
        for e in r["errors"]:
            hard_errors.append(f"slide {r['slide']} @{r['viewport']}: {e}")

    sheet = make_contact_sheet(out_dir, shots720 + shots_phone)
    report = {"deck": str(html), "slides_checked": total,
              "warnings": warnings, "errors": hard_errors,
              "contact_sheet": str(sheet) if sheet else None,
              "results": results}
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"slides: {total} | errors: {len(hard_errors)} | warnings: {len(warnings)}")
    for e in hard_errors:
        print(f"  ERROR  {e}")
    for w in warnings:
        print(f"  warn   {w}")
    print(f"artifacts: {out_dir}")
    if hard_errors:
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--slides-selector", default=".slide")
    ap.add_argument('--stage-selector', default='.stage,.deck-stage,#stage,[id*="stage"]')
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if not args.html.is_file():
        sys.exit(f"not a file: {args.html}")
    out = args.out or args.html.parent / ".preflight-check"
    out.mkdir(parents=True, exist_ok=True)
    raise SystemExit(verify(args.html, out, args.slides_selector,
                            args.stage_selector, args.limit))


if __name__ == "__main__":
    main()
