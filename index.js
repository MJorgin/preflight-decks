/**
 * DeepSeek Harness bundle for the `preflight-decks` skill.
 *
 * The repository is one skill: `SKILL.md` at the root next to its
 * `references/`, `templates/`, `scripts/`, `assets/` and `examples/`. This
 * plugin registers that same bundle with DSH's skill registry so the harness
 * lists it in the session catalog and can load it through the `skill` tool or
 * a `/preflight-decks` invocation.
 *
 * Installing the repo as a plain directory under `<dshHome>/skills/` works
 * too — `@deepseek-ai/dsh-skill-filesystem` discovers `<name>/SKILL.md`
 * bundles on its own. This bundle exists so `dsh plugin add` installs work,
 * and so the skill travels with the package.
 *
 * @module preflight-decks
 */

import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const PROVIDER_NAME = 'preflight-decks'

/**
 * Mirrors the `description` in `SKILL.md`. DSH renders it into the session
 * catalog and truncates past `catalogDescriptionMaxLength` (500 by default),
 * so it deliberately stays inside that budget.
 *
 * `scripts/check-dsh-manifest.mjs` fails when this and SKILL.md drift apart,
 * so edit both or neither.
 */
const DESCRIPTION =
  'Concept-first HTML presentation director. Use when creating or upgrading pitch decks, conference talks, internal reports, or PPTX-to-web decks. Forces a hard concept gate (three real visual directions, no reskins), then builds on a fixed 1920x1080 single-file stage, runs a scored critique loop, and proves the result with dual-viewport screenshot verification.'

const BODY = new URL('./SKILL.md', import.meta.url)

const SKILL = {
  name: 'preflight-decks',
  description: DESCRIPTION,
  body: BODY,
  invocation: { modelInvocable: true, userInvocable: true },
  provider: PROVIDER_NAME,
  source: 'bundled',
  resourceBase: {
    kind: 'directory',
    path: fileURLToPath(new URL('./', import.meta.url)),
  },
  rank: 600,
  locator: BODY,
}

const provider = {
  name: PROVIDER_NAME,
  list: () => Promise.resolve([SKILL]),
  async get(candidate) {
    const raw = await readFile(candidate.locator, 'utf8')
    // Strip the YAML frontmatter: the frontmatter is metadata for providers
    // that parse files themselves, not part of the instructions.
    const content = raw.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '')
    return {
      name: candidate.name,
      description: candidate.description,
      invocation: candidate.invocation,
      provider: candidate.provider,
      source: candidate.source,
      resourceBase: candidate.resourceBase,
      content,
    }
  },
}

/** Cordis plugin name. */
export const name = 'preflight-decks'
/** Service required by the bundled provider. */
export const inject = ['skills']

/** Register the bundled skill on DSH's skill registry. */
export async function apply(ctx) {
  ctx.skills.registerProvider(() => provider)
}
