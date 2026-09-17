#!/usr/bin/env node
/**
 * Guard the DeepSeek Harness bundle manifest against drift.
 *
 * Checks that:
 *   1. SKILL.md carries a frontmatter `name` in kebab-case and a `description`;
 *   2. that description fits DSH's catalog budget (500 chars by default) and
 *      matches the copy in index.js;
 *   3. package.json declares the DSH bundle patch and the patch file exists;
 *   4. the patch mounts the same plugin id the package is named after.
 *
 * Run: node scripts/check-dsh-manifest.mjs   (also runs in CI)
 */

import { readFile, access } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const CATALOG_MAX = 500

const problems = []
const note = (message) => problems.push(message)

const skill = await readFile(path.join(ROOT, 'SKILL.md'), 'utf8')
const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(skill)
if (!match) {
  note('SKILL.md has no YAML frontmatter')
} else {
  const frontmatter = match[1]
  const name = /^name:\s*(.+)$/m.exec(frontmatter)?.[1]?.trim()
  const description = /^description:\s*(.+)$/m.exec(frontmatter)?.[1]?.trim()

  if (!name) note('SKILL.md frontmatter is missing `name`')
  else if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name)) {
    note(`SKILL.md name "${name}" is not kebab-case (DSH rejects other spellings)`)
  }

  if (!description) {
    note('SKILL.md frontmatter is missing `description`')
  } else {
    if (description.length > CATALOG_MAX) {
      note(
        `SKILL.md description is ${description.length} chars; DSH truncates the catalog at ${CATALOG_MAX}`,
      )
    }
    const bundle = await readFile(path.join(ROOT, 'index.js'), 'utf8')
    const mirror = /const DESCRIPTION =\s*\n?\s*'([\s\S]*?)'\n/.exec(bundle)?.[1]
    if (mirror === undefined) note('index.js does not define a DESCRIPTION string')
    else if (mirror !== description) {
      note('index.js DESCRIPTION and SKILL.md description have drifted apart')
    }
  }
}

const pkg = JSON.parse(await readFile(path.join(ROOT, 'package.json'), 'utf8'))
const patch = pkg.dsh?.bundle?.patch
if (!patch) {
  note('package.json is missing dsh.bundle.patch')
} else {
  try {
    await access(path.join(ROOT, patch))
  } catch {
    note(`package.json points at ${patch}, which does not exist`)
  }
  const patchText = await readFile(path.join(ROOT, patch), 'utf8')
  if (!patchText.includes(`name: ${pkg.name}`)) {
    note(`${patch} does not mount a plugin named ${pkg.name}`)
  }
}

if (problems.length > 0) {
  console.error('DSH manifest check failed:')
  for (const p of problems) console.error(`  - ${p}`)
  process.exit(1)
}
console.log(
  `DSH bundle OK — plugin ${pkg.name}@${pkg.version}, skill description ${match[1].length > 0 ? 'in sync' : ''}`.trim(),
)
