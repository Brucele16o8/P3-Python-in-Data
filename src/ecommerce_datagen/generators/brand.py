from __future__ import annotations

from typing import Any

from faker import Faker

from ecommerce_datagen.static_data import BRANDS


def generate_brands(faker: Faker, count: int) -> list[dict[str, Any]]:
    """Generate the fixed brand dataset expected by this project."""
    if count != len(BRANDS):
        raise ValueError(f"This project expects exactly {len(BRANDS)} brands, got {count}")

    return [
        {
            "brand_name": brand_name,
            "country": country,
            "created_at": faker.date_time_this_decade(),
        }
        for brand_name, country in BRANDS
    ]
