# syntax=docker/dockerfile:1

# The FastAPI backend. Note that the root `main.py` is the uv scaffold and only
# prints a greeting — the real ASGI app is `blogs.main:app`, which is what runs
# here, matching the `uvicorn blogs.main:app` the app factory documents.
#
# Debian rather than Alpine: psycopg[binary] and cryptography publish manylinux
# wheels only, so a musl base would fall back to compiling both from source.

FROM python:3.14-slim-bookworm AS builder

# Pinned to the uv that produced uv.lock, so the build cannot drift.
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies resolve from the lockfile alone, so this layer survives every
# change that does not touch the manifests.
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY src ./src

# --no-editable installs the project as a built wheel instead of a .pth file
# pointing back at /app/src, which is what lets the runtime stage copy the
# virtualenv and nothing else. The migration .sql files travel inside the wheel.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --no-dev


FROM python:3.14-slim-bookworm AS runtime

# Settings are read from the environment under a BLOGS_ prefix at startup, so
# every value in .env.example is supplied to `docker run`, not baked in here.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN useradd --system --create-home --uid 1001 blogs

WORKDIR /app
COPY --from=builder --chown=blogs:blogs /app/.venv /app/.venv

USER blogs
EXPOSE 8000

# The app's own liveness probe: /healthz answers without touching the database,
# which is the distinction it was written for. Readiness is /readyz, and it is
# deliberately not used here — a container is not unhealthy because Postgres is
# briefly away, and restarting it would not help.
#
# The start period covers the startup the app actually does: it opens the pool
# before it binds the port and gives up after 30s, so nothing answers here until
# Postgres is reachable. Start this after the database, and give it a restart
# policy — a backend that comes up first exits rather than waiting forever.
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()"]

# Migrations are not run on startup: N replicas starting at once would race over
# the same table, and a schema change is a decision, not a side effect of a
# deploy. Run it as a one-off against the same image:
#
#   docker run --rm --env-file .env <image> python -m blogs.database.migrator up
#
# One uvicorn worker per container. Scale with replicas rather than --workers:
# the outbox poller runs per worker, so N in one container is N pollers
# competing over one table.
CMD ["uvicorn", "blogs.main:app", "--host", "0.0.0.0", "--port", "8000"]
