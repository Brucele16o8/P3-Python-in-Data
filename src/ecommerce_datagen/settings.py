from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from dotenv import load_dotenv


def _find_dotenv_path() -> Path | None:
    current = Path.cwd().resolve()
    for directory in [current, *current.parents]:
        candidate = directory / ".env"
        if candidate.exists():
            return candidate
    return None


load_dotenv(_find_dotenv_path(), override=False)


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    value = _env_str(name, str(default))
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer, got {value!r}") from exc



def _env_bool(name: str, default: bool) -> bool:
    value = _env_str(name, str(default)).lower()
    if value in {"1", "true", "yes", "y", "on"}:
        return True
    if value in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Environment variable {name} must be a boolean-like value, got {value!r}")


@dataclass(frozen=True)
class GenerationConfig:
    brands: int
    categories: int
    sellers: int
    products: int
    promotions: int
    promotion_products: int

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            brands=_env_int("GEN_BRANDS", 20),
            categories=_env_int("GEN_CATEGORIES", 10),
            sellers=_env_int("GEN_SELLERS", 25),
            products=_env_int("GEN_PRODUCTS", 2000),
            promotions=_env_int("GEN_PROMOTIONS", 10),
            promotion_products=_env_int("GEN_PROMOTION_PRODUCTS", 100),
        )


@dataclass(frozen=True)
class Settings:
    app_env: str
    db_setup_mode: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_connect_retries: int
    db_retry_delay_seconds: int
    faker_locale: str
    log_level: str
    random_seed: int | None
    batch_size: int
    reset_tables: bool
    allow_destructive_reset: bool
    generation: GenerationConfig

    @classmethod
    def from_env(cls) -> Self:
        random_seed_raw = _env_str("RANDOM_SEED", "42")
        random_seed = None if random_seed_raw == "" else int(random_seed_raw)
        return cls(
            app_env=_env_str("APP_ENV", "local"),
            db_setup_mode=_env_str("DB_SETUP_MODE", "docker_managed"),
            db_host=_env_str("DB_HOST", "localhost"),
            db_port=_env_int("DB_PORT", 5432),
            db_name=_env_str("DB_NAME", "ecommerce_oltp"),
            db_user=_env_str("DB_USER", "postgres"),
            db_password=_env_str("DB_PASSWORD", "postgres"),
            db_connect_retries=_env_int("DB_CONNECT_RETRIES", 15),
            db_retry_delay_seconds=_env_int("DB_RETRY_DELAY_SECONDS", 2),
            faker_locale=_env_str("FAKER_LOCALE", "vi_VN"),
            log_level=_env_str("LOG_LEVEL", "INFO").upper(),
            random_seed=random_seed,
            batch_size=_env_int("BATCH_SIZE", 500),
            reset_tables=_env_bool("RESET_TABLES", False),
            allow_destructive_reset=_env_bool("ALLOW_DESTRUCTIVE_RESET", False),
            generation=GenerationConfig.from_env(),
        )

    @property
    def dsn(self) -> str:
        return self.build_dsn(self.db_name)

    def build_dsn(self, db_name: str) -> str:
        return (
            f"host={self.db_host} "
            f"port={self.db_port} "
            f"dbname={db_name} "
            f"user={self.db_user} "
            f"password={self.db_password}"
        )

    @property
    def masked_dsn(self) -> str:
        return self.dsn.replace(self.db_password, "***")

    @property
    def reset_requested(self) -> bool:
        return self.reset_tables and self.allow_destructive_reset

    def validate(self) -> None:
        if self.app_env not in {"local", "development", "test", "production"}:
            raise ValueError("APP_ENV must be one of: local, development, test, production")
        if self.db_setup_mode not in {"docker_managed", "external_existing"}:
            raise ValueError("DB_SETUP_MODE must be one of: docker_managed, external_existing")
        if self.db_port <= 0:
            raise ValueError("DB_PORT must be positive")
        if self.batch_size <= 0:
            raise ValueError("BATCH_SIZE must be positive")
        if self.app_env == "production" and self.reset_tables:
            raise ValueError("RESET_TABLES is not allowed when APP_ENV=production")
        if not self.db_name.isidentifier() and "-" in self.db_name:
            raise ValueError("DB_NAME should not contain '-' for PostgreSQL unless you are prepared to quote it")
