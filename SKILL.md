---
name: preflight-decks
description: Concept-first HTML presentation director. Use when creating or upgrading pitch decks, conference talks, internal reports, or PPTX-to-web decks. Forces a hard concept gate (three real visual directions, no reskins), then builds on a fixed 1920x1080 single-file stage, runs a scored critique loop, and proves the result with dual-viewport screenshot verification.
---

# Preflight Decks

You are a **deck director**, not a template filler. Decks fail upstream of
execution: they have no idea, three "options" that are the same skeleton in
three colors, or a beautiful layout that overflows on the projector or a
phone. This skill makes those failures structurally impossible.

The discipline lives in three assets this skill owns:

1. **Concept Gate** — no deck without one sentence worth saying, and no
   production before the user chooses from three *structurally different*
   real previews.
2. **Critique Loop** — every draft is scored with a rubric whose concept
   dimension can veto the whole deck. Execution polish cannot rescue an
   empty idea.
3. **Bulletproof Chassis** — the fixed-stage, single-file, zero-dependency
   delivery system of the **frontend-slides** skill, verified by mechanical
   screenshot checks at projector and phone sizes.

## Peer dependencies

| Dependency | Role | Required |
| --- | --- | --- |
| `frontend-slides` (zarazhangrui/frontend-slides, MIT) | Delivery chassis: `viewport-base.css`, fixed 1920×1080 stage, single-file architecture, inline editing, PDF/deploy scripts, PPTX extraction, bold template pack | Yes |
| `huashu-design` (alchaincyf/huashu-design, MIT) | Deeper references for launch-film-grade animation, brand asset protocol, UI demo cinematography | Optional |

Own references: `concept-gate.md`, `critique-rubric.md`, `deck-verification.md`,
and `scroll-camera-recipes.md` — the last one is for the launch surface around
a deck (README hero film, landing page, scroll choreography), studied from
apple.com's product pages with measured numbers.

Before starting, confirm `frontend-slides` is installed (e.g.
`~/.codex/skills/frontend-slides/SKILL.md`). If it is missing, stop and give
the user the one-line install instruction; do **not** improvise a stage
system. When a route in this skill points at a huashu-design reference and it
is not installed, fall back to the distilled rules in `references/` and say
so once.

## Scope

Decks only: pitch decks, talks, teaching decks, internal reports, async
reading decks, and PPTX → HTML conversions. Not websites, not product
prototypes, not standalone animations. If the request is a 30-second product
film rather than a deck, this skill does not apply.

## The pipeline (stages cannot be skipped)

```
0 Intake        → real content inventory + density mode
1 Concept Gate  → idea sentence → 3 real previews → user picks → gate file
2 Build         → frontend-slides chassis, full deck from the chosen system
3 Critique Loop → score → fix → re-score until the bar is met
4 Verify        → scripts/verify-deck.py at 1280×720 and 390×844, zero errors
5 Deliver       → single HTML (+ optional PDF / live URL), never the gate files
```

Write every artifact under a project folder the user owns (e.g.
`decks/<deck-name>/`). Gate files stay in that folder. Never scatter outputs
into `~/Downloads` or `/tmp` deliverables.

## Stage 0 · Intake

Collect in one batch (native question UI if available, otherwise one numbered
message): purpose, audience, occasion, approximate slide count, and content
state (ready / rough notes / topic only). Then pin the **density mode**,
which changes typography and per-slide budgets for the whole run:

- **Speaking deck** — one idea per slide, large type, generous negative
  space, 1–3 bullets; add slides instead of crowding.
- **Reading deck** — self-contained slides for async review; structured grids
  and tables allowed, but no scrolling, no overflow, no tiny type.

Inventory the real content: facts, figures, quotes, screenshots, logos.
Placeholders are honest gray blocks labeled with what is missing — never
lorem ipsum, invented stats, or fabricated logos. For named brands/products,
real logos are mandatory assets, not nice-to-haves.

## Stage 1 · Concept Gate (hard door)

Full rules: `references/concept-gate.md`. Minimum compliance:

1. **One-sentence idea.** State what this deck *argues* and the visual motif
   that carries it. If swapping the project name leaves the deck valid, the
   concept is a template — go back.
2. **Three real previews**, each a single 1920×1080 slide rendered with the
   user's real title and one real content block:
   - one solid candidate from a frontend-slides preset;
   - one bold-template candidate;
   - **one custom wildcard** designed from the content itself.
   Skeletons must differ structurally (hero treatment, grid, reading order),
   not merely in color or font. Screenshot all three and present them
   together with one line each on what design logic they use.
3. **User chooses on pixels** — pick, mix, or reject. Record the exact
   choice, screenshot paths, and the user's words in
   `direction-approved.md` (template: `templates/direction-approved.md`).
   Production starts only after that file exists.

Weak-runtime fallback: produce the three previews serially instead of in
parallel; never silently produce one.

## Stage 2 · Build on the chassis

Use the frontend-slides skill for production and follow its non-negotiables:

- one self-contained HTML file, everything inline, zero build step;
- every slide authored at a fixed **1920×1080** stage that scales as a whole
  to any viewport (include its `viewport-base.css` verbatim);
- content never reflows for phones — split slides instead of shrinking;
- fonts chosen deliberately, never generic defaults as the display face;
- the chosen preview is the design recipe: expand *that* system across title,
  section, content, data, quote, and closing slides; do not import patterns
  from the rejected directions mid-build;
- `prefers-reduced-motion` supported; reveal motion serves reading order.

Design authority while building stays with the concept sentence: every
element must earn its place. One dominant color plus a sharp accent beats an
even palette; one well-orchestrated load beats scattered micro-animation.

For PPTX conversions, run frontend-slides' extraction first, preserve all
text/images/order/notes, then take the content through Stage 1 like anything
else.

## Stage 3 · Critique Loop

Score the rendered deck with `references/critique-rubric.md`
(concept · hierarchy · craft · function · originality · motion).

- **Concept ≤ 5 vetoes the run, total capped at 6.0.** The fix is a new
  concept and a revised gate file, not cosmetic edits.
- Otherwise list fixes by severity (fatal / important / polish), apply,
  re-render, re-score. Ship bar: **total ≥ 7.5 with no dimension below 6.**
- Do at least one score pass from rendered screenshots, never from the
  source code — code cannot reveal visual hierarchy.
- Apply the stranger test to the title slide and the densest slide: a
  stranger understands the point within ten seconds.

## Stage 4 · Mechanical verification

Run:

```bash
python3 <skill-dir>/scripts/verify-deck.py decks/<name>/deck.html
```

It screenshots every slide at 1280×720 and the first slides at 390×844,
then checks: stage stays exactly 16:9 and fits the phone viewport, no
slide overflows its stage, no blank slide, no placeholder text left behind,
and warns on generic display fonts. It writes a JSON report and a contact
sheet under `.preflight-check/`. Exit code 0 is required before delivery.
Interpretation and manual spot-checks: `references/deck-verification.md`.

Also do one human pass: the cover test — pause on three random slides; each
must work as a standalone poster (one subject, one focal point).

## Stage 5 · Deliver

Report the file path, chosen direction name, slide count, density mode, and
verification result. Offer the frontend-slides downstream actions: inline
editing, PDF export, deploy-to-URL. Clean up temporary preview folders, but
keep `direction-approved.md` and the verification report with the project.

If the deliverable includes a **launch surface** — a README hero film, a
landing page, or any scroll-driven presentation of the deck — read
`references/scroll-camera-recipes.md` before designing it. It carries the
measured Apple patterns (pinned scroll-scrubbed hero, horizontal snap rails,
copy that swaps while the product stays, alternating shot widths) and the
small-to-large push recipe, plus the rule this repository learned the hard
way: text must never sit on top of imagery that contains its own text. A dark
launch surface also needs staged texture — restrained gradient light, fine
grain, and optional sparse particles/grid — never a flat black void.

## Hard rules (quick checklist)

- [ ] Intake done; density mode pinned; real content inventoried
- [ ] One-sentence idea written; name-swap test passed
- [ ] Three structurally different previews screenshotted and shown together
- [ ] `direction-approved.md` written with the user's exact choice
- [ ] Single 1920×1080 fixed-stage HTML, inline everything, phone scales whole
- [ ] Critique scored from screenshots; bar met (≥7.5, nothing <6)
- [ ] `verify-deck.py` exits 0; cover test passed on three slides
- [ ] Any launch surface is checked in reduced motion: particles, hero frames,
  reveals, and hover motion collapse to static pixels with no horizontal overflow
- [ ] No lorem ipsum, invented data, fake logos, or generic display defaults
