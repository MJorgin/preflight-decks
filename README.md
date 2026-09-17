<div align="center">

# ✈️ Preflight Decks

### The concept gate for AI-built presentations.

[![CI](https://github.com/MJorgin/preflight-decks/actions/workflows/ci.yml/badge.svg)](https://github.com/MJorgin/preflight-decks/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Agent: Codex](https://img.shields.io/badge/agent-Codex-685DFF)
![Agent: Claude Code](https://img.shields.io/badge/agent-Claude%20Code-D97757)
![Agent: DSH](https://img.shields.io/badge/agent-DeepSeek%20Harness-2D664A)
![Agent: any SKILL.md](https://img.shields.io/badge/agent-any%20SKILL.md%20reader-888)

Before your agent builds the deck, you get **three structurally different
real previews** and pick on pixels. The chosen direction becomes a
single-file, fixed-stage HTML deck — and a Playwright verifier proves it fits
a 1080p projector and a phone before anyone walks into the room.

[▶ Live demo](https://mjorgin.github.io/preflight-decks/) ·
[Open the source file](./examples/preflight-decks-pitch.html) ·
[How it works](#the-pipeline) ·
[Install](#install)

</div>

![One brief becomes three structurally different real previews; the chosen direction is built into a six-slide deck and verified at projector and phone sizes](./assets/hero-concept-gate.gif)

<p align="center"><sub>
20 seconds · intake → three real directions → chosen deck → dual-viewport verification.
Every frame is this repo's own output — the concept-gate previews, the six-slide
<a href="./examples/preflight-decks-pitch.html">example deck</a>, and a real verifier
report: <b>6 slides · 2 viewports · 0 errors · 0 warnings</b>.
Shot with a camera rig: an establishing micro-push, one 1.3x push-in anchored on the
chosen direction, parallax drift over the verification wall, and a pull-back to a
full-view hold.
<a href="./assets/hero-concept-gate.mp4">MP4 version</a> ·
<a href="./docs/hero-film-storyboard.md">storyboard</a>
</sub></p>

> **Dogfooded, not aspirational.** The deck in this README was built through
> the pipeline in this repo, and the README page itself passed the same
> "what does it look like rendered, not imagined" check the skill enforces.

## Try it in 30 seconds — no install

**[Open the live demo →](https://mjorgin.github.io/preflight-decks/)** — the
same file that ships in `examples/`, served straight from `main`. Arrow keys
move through six slides.

Or run it locally:

```bash
# 1. open the deck in any browser, arrow keys to move through 6 slides
open examples/preflight-decks-pitch.html

# 2. run the same verification your decks get
python3 scripts/verify-deck.py examples/preflight-decks-pitch.html
```

One self-contained HTML file. No build step, no network, no framework. The
three pre-build directions are in
[`examples/previews/`](./examples/previews/).

## Why a gate?

Agents make decks fast. The decks still fail exactly where they always did:

1. **Nothing to say** — polished slides wrapped around an argument nobody made.
2. **Three skins** — "style options" that are one skeleton recolored three times.
3. **Fits one screen** — gorgeous on your laptop, overflowing on the projector or a phone.

Preflight Decks makes all three *impossible by construction*: no full deck
exists until you've chosen between three **structurally different** rendered
directions; every draft is scored from screenshots, and a weak concept vetoes
the run however polished the pixels; every finished deck is mechanically
verified at projector and phone sizes.

It is a thin, opinionated **judgment layer** that uses
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) (MIT) as
the delivery chassis — fixed 1920×1080 stage, single HTML file, inline
editing, PDF/URL export, PPTX conversion.

## The pipeline

```
0  Intake        content inventory + speaking vs. reading density
1  Concept gate  one argue-with sentence → 3 real previews → you pick → gate file
2  Build         full deck on the frontend-slides fixed-stage chassis
3  Critique      six-dimension scores from screenshots (bar 7.5, no dim < 6)
4  Verify        scripts/verify-deck.py — zero hard errors or no ship
5  Deliver       one HTML file (+ optional PDF / live URL)
```

## See it work

### 1. Three real directions — not three recolors

The same brief rendered three ways. Only the chosen one gets built.

![Three concept-gate previews: safe preset, bold template, wildcard field manual, with the wildcard marked chosen](./assets/demo-previews.png)

### 2. The chosen direction becomes the deck

The wildcard — a *launch preflight field manual* — becomes the six-slide pitch
deck, all in one file:

[![Six-slide example deck rendered from the single example HTML file](./assets/hero-deck.gif)](./examples/preflight-decks-pitch.html)

### 3. Verified on the room it will actually meet

Every deck is screenshotted at **1280×720** and **390×844** and checked for
overflow, elements escaping the stage, blank slides, and leftover
placeholders:

![Verification contact sheet: all six slides at projector size and the first three on a phone, all clean](./assets/verification-contact-sheet.png)

Exit code `0` = pass, `2` = hard errors, `1` = tooling problem — so the check
works in CI, not just on trust.

## What the gate adds

| Stage | What the skill forces |
| --- | --- |
| **Concept gate** | One sentence worth arguing, a motif grown from the content, and three *structurally different* previews rendered before a full deck exists |
| **Critique loop** | Six scored dimensions from actual screenshots; concept quality can veto the run |
| **Chassis** | Single fixed-stage 1920×1080 HTML file via frontend-slides — no framework, portable, editable inline |
| **Verification** | Playwright at projector + phone size: overflow, escape, blank-slide, and placeholder checks with a CI-shaped exit code |

## Install

The verifier needs Playwright and Chromium:

```bash
python3 -m pip install playwright pillow
python3 -m playwright install chromium
```

Then clone into your agent's skills directory:

```bash
# Codex (personal)
git clone https://github.com/MJorgin/preflight-decks ~/.codex/skills/preflight-decks

# Claude Code
git clone https://github.com/MJorgin/preflight-decks ~/.claude/skills/preflight-decks
```

The skill also needs its chassis peer,
[frontend-slides](https://github.com/zarazhangrui/frontend-slides):

```bash
git clone https://github.com/zarazhangrui/frontend-slides ~/.codex/skills/frontend-slides
```

Any agent that reads `SKILL.md` from a folder can use it — point the agent at
this repository and it will load only the referenced files it needs.

## Say this

```text
Make me a pitch deck for X. Don't build anything until I've picked
from three real, structurally different directions.
```

```text
Critique these slides from rendered screenshots, score all six
dimensions, and re-run the projector + phone verifier.
```

## What's in the box

```text
SKILL.md                         the orchestration contract
references/concept-gate.md       the hard door + three-direction protocol
references/critique-rubric.md    six scored dimensions, veto rules
references/deck-verification.md  what "verified" means and why
templates/direction-approved.md  the gate file the user signs off on
scripts/verify-deck.py           Playwright dual-viewport verifier
scripts/render_readme_hero.py    rebuilds the hero film above
examples/                        the dogfooded deck + its three previews
```

## Scope

Decks only — pitches, talks, teaching decks, internal reports, PPTX → HTML.
Not websites, product prototypes, or standalone product films.

## Credits

A thin opinionated layer standing on two MIT-licensed works:

- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) —
  fixed-stage single-file deck chassis, templates, export tooling.
- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) —
  the concept-first methodology and critique mindset behind the references.

Independent community project from the maker of
[github-launch-studio](https://github.com/MJorgin/github-launch-studio); not
affiliated with either upstream.

## License

[MIT](./LICENSE)
