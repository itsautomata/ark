FROM python:3.12-slim

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# install deps first (cached unless pyproject.toml or uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --python 3.12 --frozen --no-install-project

# copy source (changes here don't invalidate dep cache)
COPY ark/ ark/
COPY tests/ tests/
RUN uv sync --python 3.12 --frozen

ENTRYPOINT ["uv", "run", "ark"]
