# Use slim Python image
FROM python:3.12-slim-bookworm

# Copy pre-built uv binary from the official distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /workspaces

RUN uv venv && source .venv/bin/activate && uv pip install -e . & uv pip install -r requirements.txt
