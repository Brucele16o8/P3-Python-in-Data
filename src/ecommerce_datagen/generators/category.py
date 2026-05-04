from __future__ import annotations

from typing import Any

from faker import Faker

from ecommerce_datagen.static_data import CATEGORIES


def generate_categories(faker: Faker, count: int) -> list[dict[str, Any]]:
    """Generate the fixed two-level category dataset used by the seed pipeline."""
    if count != len(CATEGORIES):
        raise ValueError(f"This project expects exactly {len(CATEGORIES)} categories, got {count}")

    return [
        {
            "category_name": item["category_name"],
            "parent_name": item["parent_name"],
            "level": item["level"],
            "created_at": faker.date_time_this_year(),
        }
        for item in CATEGORIES
    ]
