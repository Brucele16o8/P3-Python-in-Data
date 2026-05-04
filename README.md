# E-commerce OLTP Data Generator

This project generates synthetic e-commerce data for a PostgreSQL database.

## What this project does

It creates seed data for:

- `brand`
- `category`
- `seller`
- `product`
- `promotion`
- `promotion_product`

The main command is:

```bash
uv run ecommerce-datagen seed
```

## Requirements

Install these tools first:

- Python 3.12 or 3.13
- `uv`
- Docker Desktop if you want to run PostgreSQL locally with Docker

## Step 1: Install `uv`

If you do not have `uv` installed yet, install it first.

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or with Homebrew on macOS:

```bash
brew install uv
```

Check that it is installed:

```bash
uv --version
```

## Step 2: Open the project folder

```bash
cd /path/to/ecommerce_datagen_robust_final
```

For example:

```bash
cd /Users/brucele16o8/Downloads/ecommerce_datagen_robust_final
```

## Step 3: Create the environment file

Copy the example file:

```bash
cp .env.example .env
```

The default local configuration in `.env` is:

```env
APP_ENV=local
DB_SETUP_MODE=docker_managed
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_oltp
DB_USER=postgres
DB_PASSWORD=postgres
```

## Step 4: Start PostgreSQL

You have 2 options.

### Option A: Use Docker Compose

If you want the project to run with the included Docker setup:

On macOS, make sure Docker Desktop is installed and open before running Docker commands. Wait until Docker Desktop shows that Docker is running.

```bash
docker compose up -d
```

### Option B: Use an existing PostgreSQL server

If you already have PostgreSQL installed and running outside Docker:

1. Update `.env`
2. Set the correct host, port, database, username, and password
3. Change:

```env
DB_SETUP_MODE=external_existing
```

In this mode, the database must already exist before seeding.

## Step 5: Install project dependencies

Generate the lock file and install dependencies:

```bash
uv lock
uv sync
```

## Step 6: Run the setup check

Before seeding, verify the environment and database connection:

```bash
uv run ecommerce-datagen check
```

If this fails, read the error carefully. Common causes:

- PostgreSQL is not running
- Docker Desktop is not running
- `DB_HOST`, `DB_PORT`, `DB_USER`, or `DB_PASSWORD` is wrong
- the database does not exist in `external_existing` mode

## Step 7: Seed the database

Run:

```bash
uv run ecommerce-datagen seed
```

If successful, the command will create the schema and insert seed data.

## Step 8: Run tests

```bash
uv run pytest
```

## Fast setup option

If you want one helper command for local setup, run:

```bash
bash scripts/bootstrap.sh
```

That script will:

- create `.env` if it does not exist
- start PostgreSQL with Docker Compose
- generate `uv.lock`
- install dependencies with `uv sync`

After that, run:

```bash
uv run ecommerce-datagen check
uv run ecommerce-datagen seed
uv run pytest
```

## Useful commands

Check setup:

```bash
uv run ecommerce-datagen check
```

Seed database:

```bash
uv run ecommerce-datagen seed
```

Run dependency diagnostics:

```bash
uv run ecommerce-datagen doctor
```

Run as a Python module:

```bash
uv run python -m ecommerce_datagen check
uv run python -m ecommerce_datagen seed
uv run python -m ecommerce_datagen doctor
```

## Reset seed tables safely

To truncate the seed tables before loading new data, enable both settings in `.env`:

```env
RESET_TABLES=true
ALLOW_DESTRUCTIVE_RESET=true
```

This is blocked in `production`.

## Main project files

- `pyproject.toml`: project definition
- `uv.lock`: dependency lock file generated for your machine
- `scripts/bootstrap.sh`: local setup helper
- `src/ecommerce_datagen/cli.py`: CLI entry point
- `src/ecommerce_datagen/seed.py`: seed pipeline

## Troubleshooting

### `uv run ecommerce-datagen check` says PostgreSQL is not reachable

Check:

- PostgreSQL is running
- Docker Compose containers are up if you use Docker
- port `5432` is correct
- credentials in `.env` are correct

### `uv` cannot download packages

First, retry the normal setup:

```bash
uv lock
uv sync
```

### Clean local Docker database

If you want to reset the local Docker PostgreSQL volume:

```bash
docker compose down -v --remove-orphans
docker compose up -d
```
