from __future__ import annotations

import time
from contextlib import closing
from typing import Iterator

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PGConnection

from ecommerce_datagen.settings import Settings


class DatabaseConnectionError(RuntimeError):
    """Raised when PostgreSQL cannot be reached."""


class DatabaseMissingError(RuntimeError):
    """Raised when target DB is required but missing."""


ADMIN_DB_NAME = "postgres"


def get_connection(dsn: str, *, autocommit: bool = False) -> PGConnection:
    """Open a PostgreSQL connection for the given DSN."""
    conn = psycopg2.connect(dsn)
    conn.autocommit = autocommit
    return conn


def database_exists(settings: Settings) -> bool:
    """Return whether the configured target database already exists."""
    with closing(get_connection(settings.build_dsn(ADMIN_DB_NAME), autocommit=True)) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.db_name,))
            return cur.fetchone() is not None



def wait_for_server(settings: Settings) -> None:
    """Wait until the PostgreSQL server is reachable or raise an error after retries."""
    last_error: Exception | None = None
    admin_dsn = settings.build_dsn(ADMIN_DB_NAME)
    for attempt in range(1, settings.db_connect_retries + 1):
        try:
            with closing(get_connection(admin_dsn)) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
            return
        except Exception as exc:  # pragma: no cover - depends on local postgres
            last_error = exc
            if attempt < settings.db_connect_retries:
                time.sleep(settings.db_retry_delay_seconds)
    raise DatabaseConnectionError(
        f"Could not connect to PostgreSQL server after {settings.db_connect_retries} attempts"
    ) from last_error



def create_database(settings: Settings) -> None:
    """Create the configured target database using the admin connection."""
    with closing(get_connection(settings.build_dsn(ADMIN_DB_NAME), autocommit=True)) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE DATABASE {}") .format(sql.Identifier(settings.db_name)))



def ensure_target_database(settings: Settings) -> bool:
    """Ensure the target database exists, creating it only in docker-managed mode."""
    wait_for_server(settings)
    if database_exists(settings):
        return False
    if settings.db_setup_mode == "external_existing":
        raise DatabaseMissingError(
            f"Database {settings.db_name!r} does not exist. In external_existing mode, create it first."
        )
    create_database(settings)
    return True



def wait_for_target_database(settings: Settings) -> None:
    """Wait until the configured target database accepts connections."""
    last_error: Exception | None = None
    for attempt in range(1, settings.db_connect_retries + 1):
        try:
            with closing(get_connection(settings.dsn)) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
            return
        except Exception as exc:  # pragma: no cover - depends on local postgres
            last_error = exc
            if attempt < settings.db_connect_retries:
                time.sleep(settings.db_retry_delay_seconds)
    raise DatabaseConnectionError(
        f"Could not connect to target database after {settings.db_connect_retries} attempts"
    ) from last_error
