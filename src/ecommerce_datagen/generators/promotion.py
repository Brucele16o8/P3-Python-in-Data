from __future__ import annotations

import random
from datetime import timedelta
from typing import Any

from faker import Faker

from ecommerce_datagen.static_data import PROMOTION_NAMES

PROMOTION_TYPES = ["product", "category", "seller", "flash_sale"]
DISCOUNT_TYPES = ["percentage", "fixed_amount"]


def generate_promotions(faker: Faker, count: int) -> list[dict[str, Any]]:
    """Generate promotion rows with date ranges and discount values."""
    rows: list[dict[str, Any]] = []
    for i in range(count):
        start_date = faker.date_between(start_date="-365d", end_date="+30d")
        end_date = start_date + timedelta(days=random.randint(30, 50))
        discount_type = random.choice(DISCOUNT_TYPES)
        if discount_type == "percentage":
            discount_value = round(random.choice([5, 10, 15, 20, 25, 30, 40, 50]), 2)
        else:
            discount_value = round(random.choice([10_000, 20_000, 50_000, 100_000, 200_000, 500_000]), 2)

        rows.append(
            {
                "promotion_name": PROMOTION_NAMES[i % len(PROMOTION_NAMES)],
                "promotion_type": random.choice(PROMOTION_TYPES),
                "discount_type": discount_type,
                "discount_value": discount_value,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    return rows
