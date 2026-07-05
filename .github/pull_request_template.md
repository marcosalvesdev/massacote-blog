## Summary

<!-- What changed, and why. A bullet list is usually clearer than a paragraph. -->

-

## Type of change

- [ ] `feat` — new capability
- [ ] `fix` — bug fix
- [ ] `refactor` — no behavior change
- [ ] `style` — CSS/visual only, no logic change
- [ ] `docs` — documentation only
- [ ] `chore` — deps, config, tooling
- [ ] `test` — test-only change

## Test plan

<!-- What you actually did to verify this works — not just "tests pass".
     Commands run, pages/flows exercised by hand, edge cases checked. -->

- [ ]

## Checklist

- [ ] `manage.py test` passes (or `docker compose exec web python manage.py test --noinput` if it touches the DB/ORM)
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] Migrations included, if models changed
- [ ] Docs updated, if behavior/setup changed (`README.md`, `DEVELOPMENT.md`, `CLAUDE.md`, `.env.example`)
- [ ] No secrets, credentials, or `.env` values committed

## Related issue

<!-- Closes #123, or "N/A" -->
