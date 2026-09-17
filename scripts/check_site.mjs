import {existsSync, readFileSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';

const root = process.cwd();
const pages = ['site/index.html', 'site/deck/index.html'];
const sourceDeck = resolve(root, 'examples/preflight-decks-pitch.html');
const deployedDeck = resolve(root, 'site/deck/index.html');

if (readFileSync(sourceDeck, 'utf8') !== readFileSync(deployedDeck, 'utf8')) {
  throw new Error('site/deck/index.html must stay a byte-for-byte copy of examples/preflight-decks-pitch.html');
}

for (const page of pages) {
  const file = resolve(root, page);
  if (!existsSync(file)) throw new Error(`Missing site page: ${page}`);

  const html = readFileSync(file, 'utf8');
  const references = [
    ...html.matchAll(/(?:src|href)=["']([^"']+)["']/g).map(match => match[1]),
    ...html.matchAll(/["']([^"']*assets\/[^"']+)["']/g).map(match => match[1]),
  ];

  for (const rawReference of references) {
    const reference = rawReference.split('#')[0].split('?')[0];
    if (!reference || reference.startsWith('http') || reference.startsWith('data:') ||
        reference.startsWith('mailto:') || reference.startsWith('tel:')) {
      continue;
    }

    const candidate = resolve(dirname(file), reference);
    const resolved = reference.endsWith('/') ? join(candidate, 'index.html') : candidate;
    if (!existsSync(resolved)) throw new Error(`Broken site reference in ${page}: ${rawReference}`);
  }
}

console.log('Site references OK');
