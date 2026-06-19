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
- URL structure: `post:list` is the site root; `post:create` and `post:detail` live under a shared `posts/` prefix (`PostCreateView` requires login; `PostListView`/`PostDetailView` are public). `update`/`delete` templates exist but currently have no wired views/URLs — when adding them, follow the existing `LoginRequiredMixin` + generic-view pattern used by `PostCreateView`.
- `Post` has no default `Meta.ordering`, which triggers Django's `UnorderedObjectListWarning` on the paginated list view — worth fixing (e.g. `ordering = ["-created_at"]`) before relying on feed order.

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
