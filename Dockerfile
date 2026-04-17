FROM python:3.12-slim

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# copy project files
COPY pyproject.toml uv.lock ./
COPY ark/ ark/
COPY tests/ tests/

# install dependencies
RUN uv sync --python 3.12

ENTRYPOINT ["uv", "run", "ark"]
