FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Create the user first so every later layer is owned correctly with no
# chown pass (a chown -R would duplicate the venv in a new layer).
RUN useradd --create-home --uid 1000 wayfinder \
    && mkdir -p /app/.cache && chown wayfinder:wayfinder /app /app/.cache
WORKDIR /app
USER wayfinder

# Dependencies first so code changes don't invalidate the layer.
COPY --chown=wayfinder:wayfinder pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache --no-install-project

COPY --chown=wayfinder:wayfinder src/ src/
RUN uv sync --frozen --no-dev --no-cache

# Each Deployment overrides this: python -m wayfinder.route_planner, etc.
CMD ["wayfinder", "serve-tools"]
