#!/usr/bin/env bash
set -euo pipefail

PROJECT_INDEX_URL="${UV_PROJECT_INDEX_URL:-https://pypi.org/simple}"

echo "==> Using package index: ${PROJECT_INDEX_URL}"

if [ ! -f ".env" ]; then
  echo "==> .env not found. Copying from .env.example"
  cp .env.example .env
fi

echo "==> Starting PostgreSQL with Docker Compose"
docker compose up -d

echo "==> Generating uv.lock from pyproject.toml"
uv lock --index-url "${PROJECT_INDEX_URL}"

echo "==> Syncing dependencies into .venv"
uv sync --index-url "${PROJECT_INDEX_URL}"

echo "==> Bootstrap complete"
echo "Next steps:"
echo "  uv run ecommerce-datagen check"
echo "  uv run ecommerce-datagen seed"
echo "  uv run pytest"
