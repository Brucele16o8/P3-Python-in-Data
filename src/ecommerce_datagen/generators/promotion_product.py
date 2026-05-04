from __future__ import annotations

import random
from datetime import datetime, time, timedelta
from typing import Any


def generate_promotion_products(
    promotion_rows: list[dict[str, Any]],
    product_ids: list[int],
    target_count: int,
) -> list[dict[str, Any]]:
    """Generate unique promotion-to-product links for existing promotion and product IDs."""
    if not promotion_rows or not product_ids:
        raise ValueError("promotion_rows and product_ids must not be empty")

    rows: list[dict[str, Any]] = []
    used_pairs: set[tuple[int, int]] = set()

    while len(rows) < target_count:
        promotion = random.choice(promotion_rows)
        product_id = random.choice(product_ids)
        pair = (promotion["promotion_id"], product_id)
        if pair in used_pairs:
            continue
        used_pairs.add(pair)
        created_at = datetime.combine(promotion["start_date"], time.min) + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        rows.append(
            {
                "promotion_id": promotion["promotion_id"],
                "product_id": product_id,
                "created_at": created_at,
            }
        )
    return rows
