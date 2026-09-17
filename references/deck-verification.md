# Deck Verification

The critic can hallucinate; geometry cannot. Mechanical checks are the
floor, not the ceiling.

## What `verify-deck.py` checks

1. **Stage invariants.** A 1920×1080 stage exists on every slide and the
   wrapper scales it uniformly so its rendered box is ~16:9 and fits inside
   both a 1280×720 and a 390×844 viewport — no reflow, no horizontal page
   scroll.
2. **Overflow.** For the active slide: `scrollWidth/Height` vs client size,
   plus descendant right/bottom edges against the stage rect.
3. **Blank slide.** A slide with near-zero text and almost no visible
   elements fails (renders white are the classic symptom).
4. **Placeholders.** Static scan for `lorem`, `todo`, `tbd`, `xxx`,
   `占位`, `示例文字`, and similar leftovers.
5. **Generic-font warning.** The `:root`/body/title font stack leading with
   Inter/Roboto/Arial/system-ui is a warning, never a hard fail (brand
   systems can justify it).
6. **Evidence.** Every slide screenshot at 720p, first three at phone size,
   a contact sheet (when Pillow is available), and `report.json`.

Run after every critique fix and once more immediately before delivery.
## Manual spot checks (the script cannot see meaning)

- **Cover test on three random slides**: one subject, one focal point,
  ≤3 active elements, usable as a poster if frozen.
- **Ten-second stranger test** on the title and densest slides: point at
  where the eye lands first, second, third — that must be the intended order.
- **Color meaning**: status colors carry one meaning across the deck;
  emphasis color is used sparingly enough to keep its power.
- **Numbers/dates/names**: read every figure against source material.
- **Real rendering tools only**. Trust the project's Playwright/Chromium
  pipeline; thumbnail generators that forgive line-height have shipped real
  overlaps. If a check looks suspicious, run a known-good deck through the
  same tool as a control.

## Interpreting failures

| Report | Usual cause | Fix at |
| --- | --- | --- |
| `overflow-x` on one slide | too much content for the density mode | split the slide (Stage 2) |
| all slides overflow by same px | stage wrapper / safe-area bug | chassis CSS |
| phone stage wrong aspect | reflow breakpoint or non-uniform scale | viewport-base usage |
| blank after keyboard nav | slide switch uses `display:none` or no key handler | chassis contract |
| placeholder hits | honest missing content | fill, or replace with labeled gray block |

Exit code 0 with zero errors is mandatory. Warnings need a one-line
justification in the critique notes.
