# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A personal blog (Django) for writing about tech and other topics. Currently scoped to posts (CRUD); the intended scope grows to typical blog features (comments, ratings, etc.) as the project evolves — design new apps/models with that direction in mind rather than treating `post` as the only app this project will ever have.

Frontend follows a Medium-inspired design system (serif headlines, single centered reading column, no CSS framework/build step — see `post/static/post/css/style.css` and `templates/base.html`).

## Commands

This project uses `uv` for dependency management (see `uv.lock`) with a `.venv` at the repo root.

- Run dev server: `.venv/Scripts/python manage.py runserver` (or `uv run manage.py runserver`)
- Make migrations after model changes: `.venv/Scripts/python manage.py makemigrations`
- Apply migrations: `.venv/Scripts/python manage.py migrate`
- Run tests: `.venv/Scripts/python manage.py test` (single app: `manage.py test post`)
- Django shell: `.venv/Scripts/python manage.py shell`
- Create superuser (for admin/login-gated views): `.venv/Scripts/python manage.py createsuperuser`

There is no configured linter/formatter in `pyproject.toml` yet — don't assume `ruff`/`black` are wired in.

## Architecture

- `core/` is the Django project (settings, root `urls.py`); `post/` is the first domain app. Each new blog feature (comments, ratings, etc.) should be its own app under the same pattern rather than growing inside `post`.
- Settings (`core/settings.py`) read `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` from environment via `python-decouple` (`.env` file, gitignored).
- Templates resolve from two places: the project-level `templates/` dir (`base.html`, shared layout) and each app's own `app/templates/app/` dir via `APP_DIRS`. All page templates extend `templates/base.html` and override `{% block content %}`.
- Static assets are per-app (`post/static/post/css/style.css`), picked up by Django's app-static finder — no bundler.
- `post/forms/` is a package (not a single `forms.py`); `PostForm` lives in `post/forms/post_form.py`. Follow this convention (one form per file) when adding forms rather than collapsing into a flat module.
- `Post.slug` is auto-derived from `title` inside `PostForm.clean_title` (via `slugify`), and uniqueness is enforced there with a validation error — slugs aren't editable directly through the form.
- `Post` exposes `get_excerpt()` (falls back to a 30-word truncation of `content` when no explicit `excerpt` is set) and a `reading_time` property (word count ÷ 200 wpm) — both are template-facing computed values, not stored fields beyond `excerpt` itself.
- URL structure: `post:list` is the site root; `post:create`, `post:update`, `post:delete`, and `post:detail` live under a shared `posts/` prefix. `create`/`update`/`delete` all require login (`LoginRequiredMixin`) and scope their queryset to `author=request.user`; `list`/`detail` are public.
- `account/` mirrors `post/`'s package conventions (`account/forms/`, `account/views/`) for the same reason — one form/view per file. `Profile` (bio, avatar) is a separate model with a `OneToOneField` to `auth.User`, auto-created via a `post_save` signal (`account/signals.py`, wired in `AccountConfig.ready()`) — don't assume `user.profile` needs a `get_or_create` guard, it always exists once the user does.
- Auth URLs: `django.contrib.auth.urls` and `account.urls` are both mounted at `accounts/` in `core/urls.py`, in that order — `django.contrib.auth.urls` **must** come first, since `account.urls` has a catch-all `<str:username>/` pattern that would otherwise shadow `accounts/login/`, `accounts/logout/`, etc.
- Cover images (`post`) and avatars (`account`) are both stored under a path keyed by the owning user's `username` (`post_cover_path`, `get_avatar_path`) — follow that convention for any new per-user upload field rather than keying by id or a flat directory.

## Testing

Tests use Django's built-in test framework (`django.test.TestCase`, `django.test.Client`) via `manage.py test` — no `pytest`/`pytest-django` dependency. Don't introduce one without discussing it first; it'd be a tooling change, not a test.

**Layout.** Each app's tests live in a `tests/` package, not a single `tests.py`, mirroring the `forms/`/`views/` one-thing-per-file convention already used in this repo:
```
<app>/tests/
    __init__.py
    test_models.py
    test_forms.py
    test_views.py
    test_signals.py   # only for apps with signals, e.g. account
```
Cross-app integration tests (a flow that touches more than one app — signup creating a profile then posting, password reset end-to-end, etc.) live in a top-level `tests/` package at the repo root, not bolted onto whichever app happens to start the flow. `manage.py test` discovers both locations automatically with no config.

**Arrange-Act-Assert.** Structure every test body as three blocks in that order, separated by a blank line — setup/given, the single action under test, then assertions. Don't interleave extra assertions between setup and action, and don't bury the action inside a conditional. One behavior per test method; if you need "and" to describe what a test checks, split it.

**What to hit the database for.**
- Form/validation unit tests: build unsaved instances or unbound forms where possible; only persist (`.save()`) when the behavior under test specifically depends on a DB constraint (e.g. `PostForm`'s slug-uniqueness check, which queries `Post.objects.filter(...)`).
- View tests: use `Client`/`force_login`, assert on status codes, redirects (`assertRedirects`), and resulting DB state (e.g. `Post.objects.filter(...).exists()`) — not on rendered HTML strings, except where the behavior genuinely is the markup (e.g. confirming a field renders password-masked).
- Prefer real `TestCase` DB transactions (Django wraps each test in a rollback) over mocking the ORM. Don't mock `Post.objects`/`User.objects` — that tests the mock, not the code.

**Mocking.** Mock only at real external/non-deterministic boundaries — there's nothing like that yet in this codebase (no third-party API calls). For email, don't mock `django.core.mail.send_mail` — Django's test runner already swaps `EMAIL_BACKEND` to `locmem` automatically, so assert against `django.core.mail.outbox` instead. Reach for `unittest.mock.patch` only when a real Django test utility doesn't already cover the case.

**Fixtures.** No `factory_boy` or fixture files. Use plain helper methods on the `TestCase` (or a small `setUp`) to create a `User`/`Post`/`Profile` — keep them minimal (only the fields the test actually needs) rather than building a full "realistic" object every time.

## Git commit rules

Commit when a unit of work is complete (a fix, a feature slice, a template/style change, etc.) — don't wait for explicit "commit this" requests, and don't batch unrelated changes into one commit.

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <short summary>

[optional body]
```

- **type**: `feat` (new capability), `fix` (bug fix), `refactor` (no behavior change), `style` (CSS/visual only, no logic change), `docs`, `chore` (deps, config, tooling), `test`
- **scope**: the app or area touched, e.g. `post`, `core`, `templates` — omit if it doesn't add clarity
- **summary**: imperative mood, lowercase, no trailing period (e.g. `fix(post): exclude current post from duplicate-title check`)
- Body only when the *why* isn't obvious from the summary/diff

Keep commits scoped and atomic — a model change + its migration + the form/template that depend on it can be one commit; unrelated cleanups go in their own.
