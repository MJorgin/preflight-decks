# Hero film storyboard

The README hero film (`assets/hero-concept-gate.gif` / `.mp4`) is rendered
deterministically by `scripts/render_readme_hero.py`. This is its lightweight
storyboard card — one row per shot, eight fields, written before the camera
work was implemented. Camera parameters follow the budget rules in
`camera-language.md`: push-ins below 1.25x are only allowed as the opening
establishing move, zoom durations come from the log formula
`0.55 x |ln(z2/z1)| / ln2` clamped to [0.30, 0.94]s, and no seam is a bare cut.

1280x720 stage rendered at 25fps, 496 frames (19.8s); the GIF export is
960x540 at 12.5fps.

| # | Time | 景别 | [CAMERA] move + motive | Composition (percent language) | Key motion | Transition to next | Acceptance frames |
|---|---|---|---|---|---|---|---|
| 1 | 0.0–3.6s | 全景 1x (from 1.06x) | Establishing micro-push 1.06x → 1.0 over 3.0s · "the camera is alive before anything happens"; below-1.25x is legal only here | Brief card centered 65% width, 40–78% height; step label top-left 6%; watermark top-right | Typewriter brief (1 char/2f), then the "usual result" warning bar slams in | Defocus handoff (out 0→8px, in 8→0px, 8f overlap) | f00, f89 |
| 2 | 3.6–8.2s | 中景 1.3x | Push-in 1.0x → 1.3x over 0.30s (log formula) · anchor = the chosen wildcard preview, the one object worth looking at next | Three previews at equal size across mid 45%; losers wash to paper at 66% opacity; chosen keeps cinnabar border; stamp lands centre of chosen | Staggered preview entry (8f apart), loser wash, then CHOSEN stamp slams | Flash-wash (white peak 2–4f, 5f ramps) | f135, f204 |
| 3 | 8.2–12.4s | 全景 1x / 远景 0.78x / 全景 1x | Static · the deck itself is the subject; no camera move competes with three different framings | 3a full-bleed title slide; 3b slide 03 as a 78% card on paper with shadow; 3c full-bleed score slide | Per-shot projector settle (1.03x → 1.0x over 5f) + paper flash on the two internal cuts | Defocus handoff (8f) | f240, f310 |
| 4 | 12.4–16.6s | 中景 1x + parallax | Idle drift, diagonal sine, layers at 0.35 / 0.7 / 1.4 speed ratios (far ≤4 layers) · keeps the verification wall breathing | Projector shot left 46%, phone right 16%, terminal bottom 30%; far layer = headline, mid = devices, near = terminal + stamp | Rack focus (far layer 3px → 0 over 12f), terminal lines land, CLEARED stamp | Dip-to-dark (≤0.6s total, no dwell in the dark) | f360, f414 |
| 5 | 16.6–19.8s | 全景 1x (from 1.15x) | Pull-back 1.15x → 1.0 over 0.30s, then full-view hold ≥0.8s · cold open, calm close; never end pushed-in | Two-line statement centred at 30–45% height, subtitle 54%, URL chip 62%; everything else empty paper | Title lands in two beats, subtitle, URL chip; hold | (end) | f430, f495 |

Budget check: four camera events across 19.8s (~3 per 15s window, limit 4–5);
every push-in duration comes from the log formula; all four seams carry a
transition; the film ends on a static full view.
