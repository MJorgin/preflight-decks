# Security policy

## Reporting a vulnerability

Please report vulnerabilities privately via GitHub Security Advisories
(**Report a vulnerability** on the Security tab). Do not open a public issue.

Include minimal reproduction steps and, if possible, a sample deck file.

## Scope

- `scripts/verify-deck.py` opens local HTML files in a local Playwright/Chromium
  instance. It performs no network requests and uploads no deck content.
- Deck HTML produced by agents is untrusted by definition: review it before
  opening, and run only files whose provenance you trust.
