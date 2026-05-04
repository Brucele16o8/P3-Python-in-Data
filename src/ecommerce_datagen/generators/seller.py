from __future__ import annotations

import random
from typing import Any

from faker import Faker

SELLER_TYPES = ["Official", "Marketplace"]
SELLER_TYPE_WEIGHTS = [0.35, 0.65]


def generate_sellers(faker: Faker, count: int) -> list[dict[str, Any]]:
    """Generate synthetic seller rows with realistic join dates and ratings."""
    rows: list[dict[str, Any]] = []
    for _ in range(count):
        rows.append(
            {
                "seller_name": faker.company(),
                "join_date": faker.date_between(start_date="-5y", end_date="today"),
                "seller_type": random.choices(SELLER_TYPES, weights=SELLER_TYPE_WEIGHTS, k=1)[0],
                "rating": round(random.uniform(3.0, 5.0), 1),
                "country": "Vietnam",
            }
        )
    return rows
