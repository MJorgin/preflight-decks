# Using preflight-decks in DeepSeek Harness

The repository is one skill bundle plus a DSH plugin wrapper, so the same
checkout serves Codex, Claude Code and DeepSeek Harness without a fork or a
second copy of the instructions.

| | |
|---|---|
| Skill name | `preflight-decks` (kebab-case, as DSH requires) |
| Bundle shape | `<repo>/SKILL.md` + `references/`, `templates/`, `scripts/`, `assets/`, `examples/` |
| Catalog description | 361 chars — inside DSH's 500-char `catalogDescriptionMaxLength` |
| Verified against | `@deepseek-ai/dsh-skill-filesystem` 0.1.2-alpha.2 (both install paths below) |

## Install

Either path works; pick one.

**Bundle plugin** — for `dsh plugin` managed profiles (`~/.dsh/profiles/<name>/package.json`):

```sh
dsh plugin --profile <name> add github:MJorgin/preflight-decks
```

**Plain skill directory** — nothing else to configure, DSH discovers it:

```sh
git clone https://github.com/MJorgin/preflight-decks ~/.dsh/skills/preflight-decks
```

The filesystem provider also scans `~/.agents/skills`, `<project>/.dsh/skills`
and `<project>/.agents/skills`; a clone into any of those is picked up the same
way, at that root's rank. Bundles live at depth one — DSH deliberately does
**not** discover nested `**/SKILL.md`, so the skill directory must be a direct
child of the scanned root.

### The peer skill has to be visible to DSH too

`preflight-decks` builds on [frontend-slides](https://github.com/zarazhangrui/frontend-slides)
for the fixed 1920×1080 chassis. Install it into a root DSH already scans:

```sh
git clone https://github.com/zarazhangrui/frontend-slides ~/.dsh/skills/frontend-slides
```

## What DSH does with it

- **Session catalog.** Every model-invocable skill is listed with its name and
  a length-capped description; the agent is told to load a skill by name
  before acting on a task that matches it.
- **Load path.** The `skill` tool returns the full body (frontmatter
  stripped) plus the resource base, so `scripts/verify-deck.py`,
  `references/*.md` and `templates/*` resolve against the checkout.
- **Direct invocation.** `/preflight-decks` injects the instructions into the
  current turn without the model having to load it.
- **Live updates.** The provider watches roots at depth one: adding, renaming
  or re-frontmattering a skill shows up in the next model step, no restart.
  Edits inside `references/`, `scripts/` or `assets/` are ignored by design —
  they change the body's resources, not the catalog entry.

## Runtime notes

**Verifier dependencies.** `scripts/verify-deck.py` needs Python 3, Playwright
and a Chromium build:

```sh
python3 -m pip install playwright pillow
python3 -m playwright install chromium
```

That download is ~150 MB and writes to the user cache; under DSH's bash/fs
sandbox the first run may need an approval. The verifier also writes
`<deck>/.preflight-check/` next to the deck — same story, a write outside the
workspace root needs permission.

**Subagents.** DSH ships subagent tools, so the concept gate's three directions
can be produced in parallel. The skill also defines the weak-runtime path
(serial previews) for hosts without them, and both paths end in the same
critique-and-verify loop.

**No harness-specific instructions in the body.** `SKILL.md` stays
harness-agnostic on purpose; DSH specifics live in this file and in
`index.js`, which is only the registry wrapper.

## Verifying the install

After installing, open a new session: `preflight-decks` should appear in the
skill catalog (and complete on `/preflight-decks`). To check the bundle
without the GUI:

```sh
node scripts/check-dsh-manifest.mjs   # frontmatter, description budget, patch wiring
```

The repository also keeps this honest in CI: the manifest check runs on every
push, so a description edit that would silently truncate in DSH fails the
build instead.
