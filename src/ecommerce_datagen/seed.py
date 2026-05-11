from __future__ import annotations

import random
from contextlib import closing
from typing import Any, Sequence

from faker import Faker
from psycopg2.extras import execute_values

from ecommerce_datagen.db.connection import get_connection
from ecommerce_datagen.db.schema import create_schema, truncate_seed_tables
from ecommerce_datagen.generators.brand import generate_brands
from ecommerce_datagen.generators.category import generate_categories
from ecommerce_datagen.generators.product import generate_products
from ecommerce_datagen.generators.promotion import generate_promotions
from ecommerce_datagen.generators.promotion_product import generate_promotion_products
from ecommerce_datagen.generators.seller import generate_sellers
from ecommerce_datagen.settings import Settings

Row = dict[str, Any]


def seed_database(settings: Settings) -> dict[str, int]:
    """Create schema if needed and load all generated seed data into PostgreSQL."""
    faker = Faker(settings.faker_locale)
    if settings.random_seed is not None:
        random.seed(settings.random_seed)
        Faker.seed(settings.random_seed)

    with closing(get_connection(settings.dsn)) as conn:
        conn.autocommit = False
        try:
            create_schema(conn)
            if settings.reset_requested:
                truncate_seed_tables(conn)

            brand_rows = generate_brands(faker, settings.generation.brands)
            category_rows = generate_categories(faker, settings.generation.categories)
            seller_rows = generate_sellers(faker, settings.generation.sellers)

            with conn.cursor() as cur:
                brand_id_by_name = _insert_brands(cur, brand_rows, settings.batch_size)
                _insert_categories(cur, category_rows, settings.batch_size)
                _insert_sellers(cur, seller_rows, settings.batch_size)

                product_rows = generate_products(
                    faker=faker,
                    count=settings.generation.products,
                    category_rows=category_rows,
                    brand_id_by_name=brand_id_by_name,
                    seller_ids=[row["seller_id"] for row in seller_rows],
                )
                _insert_products(cur, product_rows, settings.batch_size)

                promotion_rows = generate_promotions(faker, settings.generation.promotions)
                _insert_promotions(cur, promotion_rows, settings.batch_size)

                promotion_product_rows = generate_promotion_products(
                    promotion_rows=promotion_rows,
                    product_ids=[row["product_id"] for row in product_rows],
                    target_count=settings.generation.promotion_products,
                )
                _insert_promotion_products(cur, promotion_product_rows, settings.batch_size)

            conn.commit()
            return {
                "brand": len(brand_rows),
                "category": len(category_rows),
                "seller": len(seller_rows),
                "product": len(product_rows),
                "promotion": len(promotion_rows),
                "promotion_product": len(promotion_product_rows),
                "orders": 0,
                "order_item": 0,
            }
        except Exception:
            conn.rollback()
            raise


def _chunked(rows: Sequence[Row], batch_size: int) -> Sequence[Sequence[Row]]:
    for start in range(0, len(rows), batch_size):
        yield rows[start : start + batch_size]


def _clean_text(value: object, default: str = "") -> str:
    """
    Convert a value to a clean single-space string.

    Example:
        "  South   Korea  " -> "South Korea"
    """
    if value is None:
        return default

    cleaned = " ".join(str(value).strip().split())
    return cleaned or default


def _insert_brands(cur, brand_rows: list[dict], batch_size: int) -> dict[str, int]:
    """
    Insert brand rows safely.

    This function is idempotent:
    - New brands are inserted.
    - Existing brands do not crash the seed.
    - Existing brands still return their brand_id.
    - Required NOT NULL column `country` is always provided.
    """

    unique_brands: dict[str, tuple[str, str, object]] = {}

    for row in brand_rows:
        brand_name = _clean_text(
            row.get("brand_name") or row.get("name")
        )

        if not brand_name:
            continue

        country = _clean_text(
            row.get("country"),
            default="Unknown",
        )
        created_at = row.get("created_at")

        # Dedupe "Samsung", " samsung ", "SAMSUNG" as the same logical brand.
        key = brand_name.casefold()

        # Keep the first brand value.
        # If first country was Unknown and later one has a real country, upgrade it.
        if key not in unique_brands:
            unique_brands[key] = (brand_name, country, created_at)
        else:
            existing_name, existing_country, existing_created_at = unique_brands[key]

            if existing_country == "Unknown" and country != "Unknown":
                unique_brands[key] = (existing_name, country, existing_created_at)

    values = list(unique_brands.values())

    if not values:
        return {}

    sql = """
        INSERT INTO brand (brand_name, country, created_at)
        VALUES %s
        ON CONFLICT (brand_name)
        DO UPDATE SET
            brand_name = EXCLUDED.brand_name
        RETURNING brand_id, brand_name;
    """

    rows = execute_values(
        cur,
        sql,
        values,
        template="(%s, %s, %s)",
        page_size=batch_size,
        fetch=True,
    )

    return {
        brand_name: brand_id
        for brand_id, brand_name in rows
    }


def _insert_categories(cur, rows: list[Row], batch_size: int) -> None:
    id_by_name: dict[str, int] = {}
    top_rows = [row for row in rows if row["level"] == 1]
    child_rows = [row for row in rows if row["level"] == 2]

    for batch in _chunked(top_rows, batch_size):
        tuples = [(row["category_name"], None, row["level"], row["created_at"]) for row in batch]
        execute_values(
            cur,
            """
            INSERT INTO category (category_name, parent_category_id, level, created_at)
            VALUES %s
            RETURNING category_id
            """,
            tuples,
            page_size=batch_size,
        )
        ids = [result[0] for result in cur.fetchall()]
        for row, category_id in zip(batch, ids, strict=True):
            row["category_id"] = category_id
            id_by_name[row["category_name"]] = category_id

    for batch in _chunked(child_rows, batch_size):
        tuples = [
            (row["category_name"], id_by_name[row["parent_name"]], row["level"], row["created_at"])
            for row in batch
        ]
        execute_values(
            cur,
            """
            INSERT INTO category (category_name, parent_category_id, level, created_at)
            VALUES %s
            RETURNING category_id
            """,
            tuples,
            page_size=batch_size,
        )
        ids = [result[0] for result in cur.fetchall()]
        for row, category_id in zip(batch, ids, strict=True):
            row["category_id"] = category_id


def _insert_sellers(cur, rows: list[Row], batch_size: int) -> None:
    for batch in _chunked(rows, batch_size):
        tuples = [
            (row["seller_name"], row["join_date"], row["seller_type"], row["rating"], row["country"])
            for row in batch
        ]
        execute_values(
            cur,
            """
            INSERT INTO seller (seller_name, join_date, seller_type, rating, country)
            VALUES %s
            RETURNING seller_id
            """,
            tuples,
            page_size=batch_size,
        )
        ids = [result[0] for result in cur.fetchall()]
        for row, seller_id in zip(batch, ids, strict=True):
            row["seller_id"] = seller_id


def _insert_products(cur, rows: list[Row], batch_size: int) -> None:
    for batch in _chunked(rows, batch_size):
        tuples = [
            (
                row["product_name"], row["category_id"], row["brand_id"], row["seller_id"], row["price"],
                row["discount_price"], row["stock_qty"], row["rating"], row["created_at"], row["is_active"],
            )
            for row in batch
        ]
        execute_values(
            cur,
            """
            INSERT INTO product (
                product_name, category_id, brand_id, seller_id,
                price, discount_price, stock_qty, rating, created_at, is_active
            )
            VALUES %s
            RETURNING product_id
            """,
            tuples,
            page_size=batch_size,
        )
        ids = [result[0] for result in cur.fetchall()]
        for row, product_id in zip(batch, ids, strict=True):
            row["product_id"] = product_id


def _insert_promotions(cur, rows: list[Row], batch_size: int) -> None:
    for batch in _chunked(rows, batch_size):
        tuples = [
            (
                row["promotion_name"], row["promotion_type"], row["discount_type"],
                row["discount_value"], row["start_date"], row["end_date"],
            )
            for row in batch
        ]
        execute_values(
            cur,
            """
            INSERT INTO promotion (
                promotion_name, promotion_type, discount_type,
                discount_value, start_date, end_date
            )
            VALUES %s
            RETURNING promotion_id
            """,
            tuples,
            page_size=batch_size,
        )
        ids = [result[0] for result in cur.fetchall()]
        for row, promotion_id in zip(batch, ids, strict=True):
            row["promotion_id"] = promotion_id


def _insert_promotion_products(cur, rows: list[Row], batch_size: int) -> None:
    for batch in _chunked(rows, batch_size):
        tuples = [(row["promotion_id"], row["product_id"], row["created_at"]) for row in batch]
        execute_values(
            cur,
            """
            INSERT INTO promotion_product (promotion_id, product_id, created_at)
            VALUES %s
            RETURNING promo_product_id
            """,
            tuples,
            page_size=batch_size,
        )
        ids = [result[0] for result in cur.fetchall()]
        for row, promo_product_id in zip(batch, ids, strict=True):
            row["promo_product_id"] = promo_product_id
