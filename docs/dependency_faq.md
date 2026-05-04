# Dependency FAQ

## Why this repo does not ship a baked `uv.lock`
A lock file generated on another machine can contain exact source details that do not match your environment. This repo generates `uv.lock` locally during bootstrap so the lock matches your machine and package index.

## What file should I edit?
Edit `pyproject.toml`. Let `uv lock` regenerate `uv.lock`.

## Why keep `requirements.txt`?
It is only a simple compatibility fallback for `pip install -r requirements.txt` workflows.
