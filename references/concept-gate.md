# Concept Gate

The gate exists because "three nice options" is the default failure mode of
deck generation: competent execution of an empty idea. Every rule below is
designed to make emptiness visible *before* a full deck exists.

## 1. The idea sentence

Before any visual work, write one sentence:

> This deck argues **\<claim\>**, and proves it visually with **\<motif\>**.

The motif must come from the content — the mechanism, object, or structure
the argument is about — not from a style catalog. Examples:

- Claim: "our tool turns launch anxiety into a checklist." Motif: a
  six-step preflight rail that fills as the story advances.
- Claim: "latency compounds." Motif: one unit of delay repeated across four
  zoom levels of the same diagram.

Run two tests:

1. **Name-swap test** — replace the project/company name with a competitor's.
   If the deck still works, the visual system is generic and the concept
   scores ≤ 5.
2. **Cover test** — hide all text and logos. Does the slide still point at
   *this* subject? If every visual is interchangeable decoration, same result.

Typographic-as-system decks are exempt from the second test only when the
type treatment itself encodes the argument (scale, repetition, or structure
carrying meaning); note why.

## 2. What makes a motif real

A real motif does three jobs across the deck:

- appears on the title slide so the viewer learns the visual grammar early;
- recurs on at least three content slides in transformed-but-recognizable
  forms (index, scale, arrangement);
- closes the deck — the final slide resolves what the title opened.

A motif that shows up once is a decoration budget, not a concept.

## 3. Three previews, structurally different

Produce exactly three single-slide previews, 1920×1080, using the user's
**real** title and at least one real content block:

| Slot | Source | Job |
| --- | --- | --- |
| Safe | a frontend-slides preset matching the mood | proves legibility baseline |
| Bold | a bold-template-pack `design.md` candidate | pushes voice and layout risk |
| Wildcard | custom design derived from the motif | the only candidate with no template |

Structural difference is mandatory across all three: hero placement, grid
logic, and reading order must differ in at least two ways. Recoloring one
skeleton three times is rejected in review — the viewer must be able to tell
the versions apart with labels hidden.

Each preview must imply an expandable system (title / section / dense data /
quote / closing). A gorgeous one-off that cannot host a table is a trap.

Render all three with the actual chassis (fixed stage, the fonts and CSS the
final deck will use) and screenshot them. Present them together, each with:
the design logic in one sentence, the display typeface, the palette, and
which slot it fills. Never label a slide "custom" or "wildcard" on the
pixels.

## 4. Choice and gate file

The first valid choice is made **on rendered pixels**: pick one, mix
("bold layout + safe palette"), request changes, or reject all three. After
the choice, immediately write `direction-approved.md` using
`templates/direction-approved.md`: what was shown (with screenshot paths),
the user's exact words, the chosen design recipe (type, palette, motif,
spacing, components), and explicit non-goals.

A mix is a new, single recipe — subsequent slides follow the mix, not three
half-systems.

## 5. Iterations after the gate

Direction changes mid-build reopen the gate briefly: record what failed,
update the idea sentence, and re-confirm. Within-direction iteration (density,
copy, individual layouts) does not.
