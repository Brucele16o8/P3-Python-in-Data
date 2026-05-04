from __future__ import annotations

import random
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from faker import Faker

from ecommerce_datagen.static_data import CATEGORY_BRAND_HINTS, PRODUCT_NAME_PARTS

Money = Decimal


def money(value: float | Decimal) -> Money:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _build_product_name(faker: Faker, brand_name: str, category_name: str) -> str:
    parts = PRODUCT_NAME_PARTS.get(category_name)

    if not parts:
        parts = ["Standard", "Premium", "Smart", "Essential"]

    token_1 = random.choice(parts)
    token_2 = random.choice(parts)
    serial = faker.bothify(text="??-####").upper()

    return f"{brand_name} {token_1} {token_2} {serial}"[:200]


def _generate_price(category_name: str) -> Money:
    price_ranges = {
        "Mobile Phones": (3_000_000, 35_000_000),
        "Laptops": (8_000_000, 45_000_000),
        "Men's Wear": (150_000, 2_500_000),
        "Women's Wear": (180_000, 3_000_000),
        "Kitchen Appliances": (250_000, 8_000_000),
        "Skincare": (90_000, 2_200_000),
    }

    # Fallback protects the generator if a new category is added later.
    low, high = price_ranges.get(category_name, (100_000, 5_000_000))

    return money(random.uniform(low, high))


def _choose_brand_id(
    category_name: str,
    brand_id_by_name: dict[str, int],
) -> tuple[int, str]:
    """
    Choose a brand that fits the category when possible.

    Example:
    - Mobile Phones should prefer Apple, Samsung, Xiaomi, etc.
    - If no matching brand exists, safely fall back to any available brand.
    """

    allowed = CATEGORY_BRAND_HINTS.get(category_name)

    if allowed:
        matching_brand_names = [
            brand_name
            for brand_name in allowed
            if brand_name in brand_id_by_name
        ]

        if matching_brand_names:
            brand_name = random.choice(matching_brand_names)
            return brand_id_by_name[brand_name], brand_name

    # Fallback if:
    # - category has no hints
    # - hints exist but none of those brands were generated
    brand_name = random.choice(list(brand_id_by_name.keys()))
    return brand_id_by_name[brand_name], brand_name


def generate_products(
    faker: Faker,
    count: int,
    category_rows: list[dict[str, Any]],
    brand_id_by_name: dict[str, int] | list[dict[str, Any]],
    seller_ids: list[int],
) -> list[dict[str, Any]]:
    """Generate product rows using existing category, brand, and seller IDs."""

    if count < 0:
        raise ValueError("count must be >= 0")

    if not category_rows:
        raise ValueError("category_rows must not be empty")

    if isinstance(brand_id_by_name, list):
        brand_id_by_name = {
            row["brand_name"]: row["brand_id"]
            for row in brand_id_by_name
            if row.get("brand_name") and row.get("brand_id") is not None
        }

    if not brand_id_by_name:
        raise ValueError("brand_id_by_name must not be empty")

    if not seller_ids:
        raise ValueError("seller_ids must not be empty")

    leaf_categories = [
        row
        for row in category_rows
        if row.get("level") == 2 and row.get("category_id") is not None
    ]

    if not leaf_categories:
        raise ValueError(
            "No usable leaf categories found. "
            "Make sure _insert_categories() runs before generate_products()."
        )

    rows: list[dict[str, Any]] = []

    for _ in range(count):
        category = random.choice(leaf_categories)

        category_name = category["category_name"]

        brand_id, brand_name = _choose_brand_id(
            category_name=category_name,
            brand_id_by_name=brand_id_by_name,
        )

        price = _generate_price(category_name)

        discount_price = money(
            price * Decimal(str(random.uniform(0.70, 1.00)))
        )

        rows.append(
            {
                "product_name": _build_product_name(
                    faker=faker,
                    brand_name=brand_name,
                    category_name=category_name,
                ),
                "category_id": category["category_id"],
                "brand_id": brand_id,
                "seller_id": random.choice(seller_ids),
                "price": price,
                "discount_price": discount_price,
                "stock_qty": random.randint(0, 500),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "created_at": faker.date_time_between(
                    start_date="-3y",
                    end_date="now",
                ),
                "is_active": random.random() < 0.9,
            }
        )

    return rows
