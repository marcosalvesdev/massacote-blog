# Development

Technical documentation for the `massacote-blog` project. If you're looking for what this project *is*, see `README.md` — this doc is about how it's built and how to work on it.

## Stack

- **Backend**: Django 6, Python 3.12
- **Database**: PostgreSQL 17 (via `psycopg[binary]` — psycopg3, native Django support)
- **Static/media storage**: local filesystem in dev; Amazon S3 in production (`django-storages`), toggled by `USE_S3_STORAGE`
- **WSGI server**: Gunicorn (production/containerized runs); Django's `runserver` for local dev
- **Static file serving in production**: S3 for `staticfiles`; WhiteNoise available as a dev-only fallback to simulate that pipeline locally without S3
- **Dependency management**: [`uv`](https://docs.astral.sh/uv/), with `pyproject.toml`/`uv.lock`
- **Linting/formatting**: [`ruff`](https://docs.astral.sh/ruff/)
- **Containerization**: Docker (multi-stage `Dockerfile`: `development` and `production` targets) + `docker-compose.yml` (app + Postgres)
- **CI**: GitHub Actions (`.github/workflows/ci.yml`) — lint + test jobs, testable locally with [`act`](https://github.com/nektos/act)
- **Config**: environment variables via `python-decouple`, `.env` (gitignored) / `.env.example` (template)

Production target is AWS (ECS Fargate, RDS, S3, ALB) — this repo covers the application and its container image; infrastructure provisioning is tracked separately and isn't part of this codebase yet.

## Project structure

```
core/               # Django project: settings, root urls, wsgi/asgi
post/               # Blog posts: CRUD, cover images, draft/published workflow
account/            # User profiles (bio, avatar), one-to-one with auth.User
pages/              # Static-ish pages (About)
comment/            # Comments on posts, moderation (is_approved)
templates/          # Project-level templates (base.html, shared layout)
static/             # Project-level static assets (design system: CSS variables, layout, header/footer)
tests/              # Cross-app integration tests (flows that span more than one app)
```

Most apps follow the same internal convention: `forms/` (and, for `post`/`account`, `views/`) are packages — one file per form/view — rather than a single flat module, and `tests/` is a package mirroring that (`test_models.py`, `test_forms.py`, `test_views.py`, etc.) rather than a single `tests.py`.

App-specific static assets live under each app's own `static/<app>/` directory (e.g. `post/static/post/css/`) and are loaded per-template via the `extra_css` block, rather than growing the global stylesheet.

Full conventions (URL structure, model/form patterns, template block usage, testing philosophy) are documented in `CLAUDE.md`.

## Getting started

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Docker + Docker Compose (recommended path — see below)

### Environment

Copy the template and fill in real values:

```bash
cp .env.example .env
```

At minimum, `SECRET_KEY` is required (no insecure default is provided). Everything else has a sane default for local development.

### Running with Docker Compose (recommended)

This runs the app against a real PostgreSQL instance, matching production more closely than SQLite would:

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`. Migrations and static file collection run automatically on startup (see `entrypoint.sh`).

To provision the whole thing in one shot — build the image, start the app and database, and seed it with fake data — use the Makefile shortcut instead:

```bash
make provision
```

### Running locally without a container

```bash
uv sync
uv run manage.py migrate
uv run manage.py runserver
```

Without `DATABASE_URL` pointing at a reachable Postgres instance, the app falls back to SQLite automatically — fine for a quick local check, but you're then responsible for confirming any Postgres-specific behavior still holds if you touch the ORM.

### Seeding fake data

Two management commands generate fake users, posts, and comments so there's something to look at right away — posts are seeded as published and approved, so they show up on the site immediately:

```bash
# containerized
docker compose exec web python manage.py seed_posts --clear
docker compose exec web python manage.py seed_comments --clear

# local
uv run manage.py seed_posts --clear
uv run manage.py seed_comments --clear
```

Both accept `--clear-only` (wipe without reseeding) and count overrides (`--users`, `--posts`, `--comments`) — see `--help` on each for details. `seed_comments` expects posts to already exist, so run `seed_posts` first.

**Logging in as a seeded user**: every fake user gets the same password, `pass1234`. Usernames are randomly generated (e.g. `carolbrown534`), so grab one from the `seed_posts` output — it prints `Created user: <username>` for each one it creates — or look it up via `make dshell`/`make shell`:

```python
from django.contrib.auth import get_user_model
get_user_model().objects.values_list("username", flat=True).first()
```

### Creating a superuser

You'll need one to access `/admin/` and inspect data directly:

```bash
# containerized
docker compose exec web python manage.py createsuperuser

# local
uv run manage.py createsuperuser
```

### Makefile shortcuts

A `Makefile` wraps all of the commands above (local and containerized variants, plus `provision`, `seed`/`dseed`, `createsuperuser`/`dcreatesuperuser`, test/lint/coverage/CI shortcuts). Run `make help` for the full list.

## Testing

Tests use Django's built-in test framework (`manage.py test`) — no `pytest`. Run them against the real Postgres service for anything that matters:

```bash
docker compose exec web python manage.py test --noinput
```

Coverage:

```bash
docker compose exec web coverage run manage.py test --noinput
docker compose exec web coverage report -m
```

Test layout: each app has its own `tests/` package; tests that cross app boundaries (e.g. signup → profile creation → posting) live in the top-level `tests/` package instead of being attached to whichever app happens to start the flow.

## Linting and formatting

```bash
uv run ruff check .
uv run ruff format .        # apply
uv run ruff format --check . # verify only, no changes (what CI runs)
```

## CI

`.github/workflows/ci.yml` runs a `lint` job (ruff check + format check) and a `test` job (full test suite against a `postgres:17` service container) on every push/PR to `main`.

To run the workflow locally before pushing:

```bash
act            # full workflow
act -j lint    # just the lint job
act -j test    # just the test job
```

## Key environment variables

See `.env.example` for the full list with placeholder values. Notable ones:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key — required, no default |
| `DEBUG` | Defaults to `False`; set `True` for local dev |
| `DATABASE_URL` | Parsed via `dj-database-url`; falls back to SQLite if unset |
| `USE_S3_STORAGE` | Switches media/static storage backend to S3 |
| `AWS_STORAGE_BUCKET_NAME` / `AWS_S3_REGION_NAME` | S3 bucket config (only read when `USE_S3_STORAGE=True`) |
| `ENABLE_DEBUG_TOOLBAR` | Toggles `django-debug-toolbar` independently of `DEBUG` |
| `ENABLE_WHITENOISE` | Opt-in only — serves collected static files via WhiteNoise, for locally simulating the production static pipeline without S3 |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`, `CSRF_TRUSTED_ORIGINS` | Production hardening, all off/empty by default so local HTTP dev keeps working |

## Health check

`GET /healthz/` returns a plain `200 OK`. Deliberately shallow (no database check) — it's meant for a load balancer's liveness probe, not a full system diagnostic.
