# Contributing

Thanks for your interest in Preflight Decks.

## Good first contributions

- A failing real-world deck the verifier should catch (anonymized HTML +
  expected error).
- Verifier checks for new failure modes (see `references/deck-verification.md`).
- Documentation and examples in other languages.
- Issues with screenshots showing a deck the concept gate would have saved.

## Pull requests

1. Keep scope to decks — this project intentionally does not become a general
   website/prototype/animation studio.
2. The pipeline in `SKILL.md` is the product; changes that weaken the concept
   gate or the ship bar need a clear rationale.
3. If you change `scripts/verify-deck.py`, make sure CI passes and add a
   fixture demonstrating the new behavior.
4. Run `python3 -m py_compile scripts/verify-deck.py` locally.

## Attribution

This project is an orchestration layer over MIT-licensed
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) and
[huashu-design](https://github.com/alchaincyf/huashu-design). Keep upstream
attribution intact.
