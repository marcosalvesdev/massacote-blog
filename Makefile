.PHONY: help \
	run migrate makemigrations shell createsuperuser test coverage lint format format-check seed \
	up down build logs provision \
	drun dmigrate dmakemigrations dshell dtest dcoverage dcreatesuperuser dseed \
	ci ci-lint ci-test

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

## --- Local (no container, uses .venv via uv) ---
## Talks to Postgres only if DATABASE_URL is reachable from the host;
## otherwise falls back to SQLite (see CLAUDE.md).

run: ## Run the dev server locally
	uv run manage.py runserver

migrate: ## Apply migrations locally
	uv run manage.py migrate

makemigrations: ## Create migrations locally
	uv run manage.py makemigrations

shell: ## Open the Django shell locally
	uv run manage.py shell

createsuperuser: ## Create a superuser locally
	uv run manage.py createsuperuser

test: ## Run tests locally (falls back to SQLite outside docker-compose's network)
	uv run manage.py test

coverage: ## Run tests locally with coverage report
	uv run coverage run manage.py test
	uv run coverage report -m

seed: ## Seed the local database with fake users, posts, and comments
	uv run manage.py seed_posts --clear
	uv run manage.py seed_comments --clear

lint: ## Run ruff lint checks
	uv run ruff check .

format: ## Apply ruff formatting
	uv run ruff format .

format-check: ## Check ruff formatting without writing changes
	uv run ruff format --check .

## --- Docker Compose (app + real Postgres) ---

up: ## Start app + db (foreground)
	docker compose up

build: ## Rebuild images and start app + db
	docker compose up --build

down: ## Stop and remove containers
	docker compose down

logs: ## Tail web service logs
	docker compose logs -f web

provision: ## Build, start, and seed the whole application from scratch (migrations run automatically via entrypoint.sh)
	docker compose up --build -d
	@echo "Waiting for the web service to finish migrating/collecting static..."
	@sleep 5
	$(MAKE) dseed
	@echo ""
	@echo "Done. App running at http://localhost:8000"
	@echo "Run 'make dcreatesuperuser' to create an admin account."

drun: ## Ensure containers are up (detached)
	docker compose up -d db web

dmigrate: drun ## Apply migrations inside the web container
	docker compose exec web python manage.py migrate

dmakemigrations: drun ## Create migrations inside the web container
	docker compose exec web python manage.py makemigrations

dshell: drun ## Open the Django shell inside the web container
	docker compose exec web python manage.py shell

dcreatesuperuser: drun ## Create a superuser inside the web container
	docker compose exec web python manage.py createsuperuser

dtest: drun ## Run tests inside the web container against real Postgres
	docker compose exec web python manage.py test --noinput

dcoverage: drun ## Run tests with coverage inside the web container
	docker compose exec web coverage run manage.py test --noinput
	docker compose exec web coverage report -m

dseed: drun ## Seed the containerized database with fake users, posts, and comments
	docker compose exec web python manage.py seed_posts --clear
	docker compose exec web python manage.py seed_comments --clear

## --- CI (GitHub Actions, run locally via act) ---

ci: ## Run the full CI workflow locally via act
	act

ci-lint: ## Run only the lint job locally via act
	act -j lint

ci-test: ## Run only the test job locally via act
	act -j test
