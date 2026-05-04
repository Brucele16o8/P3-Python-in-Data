from __future__ import annotations

from ecommerce_datagen.settings import Settings


def test_settings_build_dsn(monkeypatch) -> None:
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "demo")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    settings = Settings.from_env()
    assert "dbname=demo" in settings.dsn
    assert "secret" not in settings.masked_dsn
