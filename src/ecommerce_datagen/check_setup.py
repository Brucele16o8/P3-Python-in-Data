from __future__ import annotations

from ecommerce_datagen.db.connection import database_exists, wait_for_server
from ecommerce_datagen.settings import Settings


def run_check() -> int:
    """Validate settings and report PostgreSQL reachability for the current environment."""
    settings = Settings.from_env()
    settings.validate()

    print("Setup summary")
    print("-------------")
    print(f"APP_ENV={settings.app_env}")
    print(f"DB_SETUP_MODE={settings.db_setup_mode}")
    print(f"DB target={settings.db_name} on {settings.db_host}:{settings.db_port}")
    print(f"RESET_TABLES={settings.reset_tables}")
    print(f"ALLOW_DESTRUCTIVE_RESET={settings.allow_destructive_reset}")

    try:
        wait_for_server(settings)
        print("PostgreSQL server is reachable.")
    except Exception as exc:
        print(f"PostgreSQL server is not reachable yet: {exc}")
        return 1

    exists = database_exists(settings)
    if exists:
        print(f"Database '{settings.db_name}' exists.")
    else:
        print(f"Database '{settings.db_name}' does not exist yet.")
        if settings.db_setup_mode == "docker_managed":
            print("Expected action: the app can create it automatically in docker_managed mode.")
        else:
            print("Expected action: ask the customer/DBA to create the database first.")
    return 0
