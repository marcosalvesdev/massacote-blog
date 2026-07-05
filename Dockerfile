FROM python:3.12-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim-trixie AS development

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /bin/uv /bin/uvx /bin/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --group dev --frozen --no-install-project

COPY . .

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.12-slim-trixie AS production

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY . .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "core.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "2", \
    "--worker-class", "gthread", \
    "--threads", "2", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "50", \
    "--timeout", "120", \
    "--graceful-timeout", "30", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
