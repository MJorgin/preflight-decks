# The product-page shot list: what apple.com actually ships

Apple's product pages read like films because they are built from a small,
repeated set of camera patterns — and the class names in their own markup say
which one is running. Every number below was measured in a real 1440x900
Chromium session on `apple.com/iphone-18-pro/` and `apple.com/macbook-pro/`,
not estimated from screenshots.

Two pages, for scale: **37.3 viewports of scroll** (iPhone 18 Pro, 33,531px)
and **34.3 viewports** (MacBook Pro, 30,873px).

## Stage texture: the background is a set, not a paint bucket

A flat black page reads as unfinished even when the foreground is correct.
Premium product pages give the stage measurable depth before the product
enters:

- at least one large, low-contrast radial wash plus a cooler counter-light;
- a fixed film-grain/noise layer around 4–6% opacity, never tiled loudly;
- optional sparse particles or constellation lines (budget: ~82 desktop,
  ~42 mobile) that drift slower than the reader's eye and sit below all copy;
- one perspective grid or technical field in the hero, masked to fade before
  it reaches body text;
- double-bezel product frames: translucent outer tray, hairline, inset
  highlight, then the media itself.

Keep the palette to OLED black, one warm light, and one brand signal color.
The texture should make the headline feel lit by the scene; if it raises
perceived complexity or competes with text, reduce opacity rather than adding
more effects. Particle/noise layers are fixed, pointer-events none, remain
static under `prefers-reduced-motion`, and must not create horizontal
overflow or change the media's exact 16:9 crop.

Reduced-motion acceptance is mechanical, not vibes: after emulating
`prefers-reduced-motion: reduce`, wait 500ms, capture the particle canvas and
hero frame, scroll roughly one viewport, wait again, and require both captures
to be unchanged. The hero poster must remain fully opaque, the film frame must
stay at 0, reveal transforms must collapse, and both desktop and mobile
viewports must report zero horizontal overflow.

## The catalogue

### 1 · Pinned stage + scroll-scrubbed video
**Their markup:** `pin` (371 occurrences), `pin-offset`, `pin-center`,
`video-element-stack`, `scrub`, `sticky-container`.

**Measured:** the hero is a `<video>` (5.0s, `muted`, **`autoplay: false`**)
inside a sticky stage of 1440x901 — a full viewport. Its `currentTime` follows
the scroll: at scrollY 0 / 900 / 1800 the hero read **4.53 → 5.00 → (next clip)
0.71**, and the following video tracked 0 → 0.71 → 1.97. Nothing autoplays;
your scroll *is* the dolly.

**Perceptual job:** the visitor controls the camera, so the page feels like a
film they are operating rather than a page they are reading.

**Our implementation:** `position: sticky` stage, ~1 viewport of scroll per
clip, `video.currentTime = progress * duration` inside a rAF loop driven by
`IntersectionObserver`-gated scroll progress. Never `autoplay` on the scrubbed
clip.

### 2 · Horizontal rail: vertical scroll becomes sideways camera
**Their markup:** `scroll-container` + `scroll-snap-type: x mandatory`.

**Measured (iPhone 18 Pro):** five rails, each 1440px wide but **3,092–4,592px
of content — 2.1x to 3.2x the viewport**. MacBook Pro runs one at 2,700px
(1.9x). `.product-list` uses `scroll-snap-type: inline` at 1,404 / 1,022px.

**Perceptual job:** the "下拉左右滑动" the eye reads as a camera pan across a
row of objects — one gesture, many subjects, each snapping to rest.

**Our implementation:** `display: flex; overflow-x: auto; scroll-snap-type: x
mandatory` with `scroll-snap-align: center` children sized 60–80% of the
viewport, plus a right-edge fade so the rail reads as continuing off-frame.
Attach a thin progress bar and arrow-key support; never hijack the wheel.

### 3 · Staggered entry
**Their markup:** `data-staggered-item` (128 instances on iPhone, 56 on
MacBook).

**Measured:** entry is per-item, delayed, and only ever fires as the group
crosses the viewport — the same "one orchestrated entrance" our animation
pitfalls file demands, at page scale.

**Our implementation:** one `IntersectionObserver` per group; children get
`transition-delay: calc(var(--i) * 70ms)`, animating only `transform` and
`opacity`.

### 4 · Copy swaps while the product stays
**Their markup:** the sticky stage plus sibling text sections — the media is
pinned, the copy is not.

**Perceptual job:** the product becomes the constant and the feature list
becomes the variable, which is the opposite of a normal page and reads as
"one continuous demonstration".

**Our implementation:** a two-column section where the left column is
`position: sticky; top: 15vh` and the right column holds 3–5 short blocks,
each ~1 viewport tall; the pinned media swaps its `currentTime` or its frame
per block.

### 5 · Scale choreography between sections
**Measured widths:** **100% → 88% (1260px) → 52% (748px) → 100% (canvas)**.
No two adjacent sections share a framing.

**Perceptual job:** the page never reads as "stacked blocks" because the
camera distance changes at every cut.

**Our implementation:** set a per-section media width token
(`--shot: 100 | 88 | 52`) and forbid two adjacent sections from sharing it.
This is the page-level version of the deck rule "no two identical shot sizes
in a row".

### 6 · Text metrics that hold the film together
**Measured:** hero headline 80px / weight 700 / **letter-spacing -1.2px** /
line-height 1.05; text column 980px (**68%** at 1440); media column 1260px
(**87.5%**); section padding 140px+.

**Our implementation:** those two widths — 68% for copy, 87.5% for media —
and negative tracking on anything above ~48px.

### 7 · Frames stacked under the video
**Their markup:** `hero_startframe__*.jpg` + `hero_endframe__*.jpg` behind the
hero `<video>`, inside `pin-offset`.

**Perceptual job:** no flash of empty box while the clip buffers; the scroll
feels continuous from the first pixel of scroll.

**Our implementation:** render the film's first and last frame as stills,
stack them behind the `<video>`, and only reveal the video after
`loadeddata`.

### 8 · Keyframe-driven footer
**Their markup:** `data-download-area-keyframe` (144 instances).

**Perceptual job:** even the utility block at the bottom gets a scripted
scroll entrance instead of just appearing.

**Our implementation:** a small keyframe list (`[{at: 0.0, y: 40, o: 0},
{at: 0.6, y: 0, o: 1}]`) interpolated from section progress.

## Applying all of it to our landing page

| Section | Pattern | Shot width |
| --- | --- | --- |
| Hero | pinned scrub of the hero film (1) + stacked frames (7) | 100% |
| Three directions | horizontal rail with snap (2) | 100% rail, 62% frames |
| Verification | copy swaps over a pinned phone+projector still (4) | 88% |
| Deck gallery | staggered grid (3) | 52% |
| Close | keyframe footer (8) | 100% |

Rhythm rules we keep: never two adjacent sections at the same shot width, one
orchestrated entrance per group, and `prefers-reduced-motion` swaps scrubbing
and snapping for stills and a plain vertical stack.

## What we deliberately do not copy

- 34–37 viewports of scroll for a repository page. Our landing page targets
  ~6–8 viewports: same grammar, a fraction of the length.
- Silent autoplay hero video. The README asset stays a GIF; the landing page
  scrubs on demand.
- Wheel hijacking. We keep native scroll and native snapping; the page never
  takes the scrollbar away from the visitor.
