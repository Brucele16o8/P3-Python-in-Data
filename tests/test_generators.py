from __future__ import annotations

import random
from datetime import date, datetime

import pytest
from faker import Faker

from ecommerce_datagen.generators.brand import generate_brands
from ecommerce_datagen.generators.category import generate_categories
from ecommerce_datagen.generators.product import generate_products
from ecommerce_datagen.generators.promotion import generate_promotions
from ecommerce_datagen.generators.promotion_product import generate_promotion_products
from ecommerce_datagen.generators.seller import generate_sellers

SEED = 42


@pytest.fixture(autouse=True)
def fixed_seed() -> None:
    random.seed(SEED)
    Faker.seed(SEED)


@pytest.fixture
def faker() -> Faker:
    return Faker()


class TestBrand:
    def test_count(self, faker: Faker) -> None:
        assert len(generate_brands(faker, 20)) == 20

    def test_types(self, faker: Faker) -> None:
        row = generate_brands(faker, 20)[0]
        assert isinstance(row["brand_name"], str)
        assert isinstance(row["country"], str)
        assert isinstance(row["created_at"], datetime)


class TestCategory:
    def test_count(self, faker: Faker) -> None:
        assert len(generate_categories(faker, 10)) == 10

    def test_hierarchy(self, faker: Faker) -> None:
        rows = generate_categories(faker, 10)
        assert any(row["level"] == 1 for row in rows)
        assert all(row["parent_name"] is None for row in rows if row["level"] == 1)
        assert all(row["parent_name"] is not None for row in rows if row["level"] == 2)


class TestSeller:
    def test_country(self, faker: Faker) -> None:
        assert all(row["country"] == "Vietnam" for row in generate_sellers(faker, 5))

    def test_join_date_type(self, faker: Faker) -> None:
        assert isinstance(generate_sellers(faker, 1)[0]["join_date"], date)


class TestProduct:
    def test_relationship_fields(self, faker: Faker) -> None:
        brand_rows = generate_brands(faker, 20)
        for index, row in enumerate(brand_rows, start=1):
            row["brand_id"] = index
        category_rows = generate_categories(faker, 10)
        next_id = 1
        id_by_parent: dict[str, int] = {}
        for row in category_rows:
            row["category_id"] = next_id
            if row["level"] == 1:
                id_by_parent[row["category_name"]] = next_id
            next_id += 1
        rows = generate_products(faker, 50, category_rows, brand_rows, [1, 2, 3])
        assert len(rows) == 50
        assert all(row["discount_price"] <= row["price"] for row in rows)
        assert all(0 <= row["stock_qty"] <= 500 for row in rows)


class TestPromotion:
    def test_dates(self, faker: Faker) -> None:
        rows = generate_promotions(faker, 10)
        assert all(row["end_date"] > row["start_date"] for row in rows)


class TestPromotionProduct:
    def test_unique_pairs(self) -> None:
        promotion_rows = [{"promotion_id": 1, "start_date": date(2024, 1, 1)}, {"promotion_id": 2, "start_date": date(2024, 1, 2)}]
        rows = generate_promotion_products(promotion_rows, list(range(1, 101)), 20)
        pairs = {(row["promotion_id"], row["product_id"]) for row in rows}
        assert len(rows) == len(pairs)
