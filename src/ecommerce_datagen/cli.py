from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.table import Table

from ecommerce_datagen.check_setup import run_check
from ecommerce_datagen.db.connection import ensure_target_database, wait_for_target_database
from ecommerce_datagen.doctor import run_doctor
from ecommerce_datagen.logging_utils import configure_logging
from ecommerce_datagen.seed import seed_database
from ecommerce_datagen.settings import Settings

console = Console()


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the project CLI."""
    parser = argparse.ArgumentParser(
        prog="ecommerce-datagen",
        description="Generate synthetic e-commerce OLTP seed data for PostgreSQL.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("check", help="Check environment and database reachability.")
    subparsers.add_parser("doctor", help="Inspect likely package index config sources.")

    seed_parser = subparsers.add_parser("seed", help="Create database/schema and seed data.")
    seed_parser.add_argument("--json", action="store_true", help="Print summary as JSON.")

    parser.set_defaults(command="seed")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI command and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        return run_check()
    if args.command == "doctor":
        return run_doctor()

    settings = Settings.from_env()
    settings.validate()
    log = configure_logging(settings.log_level)

    log.info(f"Startup mode: APP_ENV={settings.app_env}, DB_SETUP_MODE={settings.db_setup_mode}")
    log.info(f"Connecting to PostgreSQL with {settings.masked_dsn}")

    created = ensure_target_database(settings)
    if created:
        log.info(f"Created database '{settings.db_name}'.")
    wait_for_target_database(settings)
    log.info("Database connection OK")

    if settings.reset_tables and not settings.allow_destructive_reset:
        log.warning(
            "RESET_TABLES=true was requested, but ALLOW_DESTRUCTIVE_RESET is not enabled. "
            "Skipping truncate for safety."
        )
    elif settings.reset_requested:
        log.warning("Destructive reset is enabled for this run. Seed tables will be truncated first.")

    summary = seed_database(settings)
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    table = Table(title="Seed Summary")
    table.add_column("Table", style="bold cyan")
    table.add_column("Rows", justify="right", style="green")
    for key, value in summary.items():
        table.add_row(key, str(value))
    console.print(table)
    console.print("Orders and order_item are intentionally left at 0 for this phase.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
