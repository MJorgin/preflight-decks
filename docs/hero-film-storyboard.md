# Hero film storyboard

`assets/hero-concept-gate.gif` / `.mp4` is rendered deterministically by
`scripts/render_readme_hero.py`. This is its shot list, written in the
vocabulary of `references/scroll-camera-recipes.md` — the grammar measured
from apple.com's product pages.

**Direction C · cinematic instrument stage.** OLED near-black gradient, warm
signal light, one cool counter-light, SF Pro for display type, SF Mono for
labels, amber eyebrows, signal-red accent. Product screenshots sit in nested
glass bezels with soft floor shadows; the selected card gets a restrained red
halo. The set also carries a sparse particle/constellation field, a masked
perspective grid and fixed film grain, matching the live launch page while
leaving the real slides as the dominant focal points.

1280×720 master at 25fps, 496 frames (19.84s); GIF export 960×540 at 12.5fps,
48-colour palette, no dither (measured: text and screenshots stay legible;
the richer stage is ~5.6 MiB, suitable for a GitHub README).

| # | Time | Shot | Camera move + motive | Composition | Transition to next | Acceptance frames |
|---|---|---|---|---|---|---|
| 1 | 0.0–3.6s | 全景 1x (from 1.06x) | Establishing micro-push, 1.06x → 1.0 over 3.0s — the frame is alive before anything happens; below-1.25x is legal only here | Split intake: the three failure modes on the left, the actual brief in a nested editor chrome on the right | Defocus handoff (0→8px, 8f overlap) | f00, f89 |
| 2 | 3.6–8.2s | 全景 1x → 中景 1.3x | **Lateral pan** across the rail (+392px, 40f) then a 1.3x push anchored on the chosen direction — Apple's horizontal-rail language | Three floating previews across the mid band; losers dim into the stage; selected card carries a red halo and precision badge | Warm light wash (38% peak, 5f ramps) | f135, f204 |
| 3 | 8.2–12.4s | 52% → 100% | **The push**: one continuous 52% → 100% move (ease-in-out, 0.18–0.72 of the shot), with a cross-dissolve from chosen preview to deck during 0.12–0.42 of the shot — the move is authored into the render, not faked with CSS | Real preview resolves into the built deck inside a glass bezel that reaches full bleed; copy has left the frame by the time the panel is large | Defocus handoff (8f) | f240, f310 |
| 4 | 12.4–16.6s | 88% | Static, parallax drift on the verification wall (far/mid/near layers) | Projector screen, physical phone, and a compact verifier receipt share the same bezel language, with the real numbers | Dip-to-OLED (≤0.6s total) | f360, f414 |
| 5 | 16.6–19.8s | 全景 1x (from 1.15x) | Pull-back 1.15x → 1.0, then a static full-view hold ≥0.8s — never end pushed-in | Two-line statement, three mechanism chips and a URL chip on an otherwise empty stage | (end) | f430, f495 |

Budget check: four camera events across 19.8s; every push-in duration comes
from the log formula; all four seams carry a designed transition; the film
ends on a static full view. Verified after render: the build shot measures
52.0% → 65.6% → 95.2% → 100% panel width across frames 210/240/275/310, and
no text box intersects an image box in any shot.

## Rebuilding

```bash
python3 scripts/render_readme_hero.py
```

The verifier screenshots the film is cut from are generated, not committed; the
script runs `scripts/verify-deck.py` first when they are missing. The stage is
deterministic, so a fresh clone rebuilds the same film without random particle
or grain flicker.

## Launch-page assets derived from the master film

The live launch page (`site/`) reuses this film's full arc instead of keeping
its own cut:

```bash
# 72-frame WebP sprite for scroll scrubbing + first/last fallback JPEGs
# (requires ffmpeg; samples evenly across all five shots, so the site can
# silently drift to a two-clip recut no more)
python3 scripts/render_site_filmstrip.py

# rail + pinned screenshots, floated as lit screens on the matching dark set
python3 scripts/render_site_previews.py

# 1280x640 OG/Twitter card with the launch headline and the chosen direction
python3 scripts/render_site_social_card.py   # macOS (system SF Pro)
```

Preview sources live in `assets/site-previews/`; all three outputs land in
`site/assets/`, are committed, and are never rebuilt in CI.
