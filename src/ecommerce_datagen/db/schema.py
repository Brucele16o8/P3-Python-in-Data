from __future__ import annotations

from psycopg2.extensions import connection as PGConnection

SCHEMA_SQL = """
BEGIN;

CREATE TABLE IF NOT EXISTS brand (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INT NULL REFERENCES category(category_id) ON DELETE SET NULL,
    level SMALLINT NOT NULL CHECK (level IN (1, 2)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_category_name_parent UNIQUE (category_name, parent_category_id)
);

CREATE TABLE IF NOT EXISTS seller (
    seller_id SERIAL PRIMARY KEY,
    seller_name VARCHAR(150) NOT NULL,
    join_date DATE NOT NULL,
    seller_type VARCHAR(50) NOT NULL CHECK (seller_type IN ('Official', 'Marketplace')),
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 0 AND rating <= 5),
    country VARCHAR(50) NOT NULL DEFAULT 'Vietnam'
);

CREATE TABLE IF NOT EXISTS product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT NOT NULL REFERENCES category(category_id),
    brand_id INT NOT NULL REFERENCES brand(brand_id),
    seller_id INT NOT NULL REFERENCES seller(seller_id),
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    discount_price DECIMAL(12,2) NOT NULL CHECK (discount_price >= 0 AND discount_price <= price),
    stock_qty INT NOT NULL CHECK (stock_qty >= 0),
    rating FLOAT NOT NULL CHECK (rating >= 0 AND rating <= 5),
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
    order_id BIGSERIAL PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    seller_id INT NOT NULL REFERENCES seller(seller_id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PLACED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')),
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_item (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES product(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(12,2) NOT NULL CHECK (subtotal >= 0)
);

CREATE TABLE IF NOT EXISTS promotion (
    promotion_id SERIAL PRIMARY KEY,
    promotion_name VARCHAR(100) NOT NULL,
    promotion_type VARCHAR(50) NOT NULL CHECK (promotion_type IN ('product', 'category', 'seller', 'flash_sale')),
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount')),
    discount_value NUMERIC(10,2) NOT NULL CHECK (discount_value > 0),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT chk_promotion_date_range CHECK (end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS promotion_product (
    promo_product_id SERIAL PRIMARY KEY,
    promotion_id INT NOT NULL REFERENCES promotion(promotion_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_promotion_product UNIQUE (promotion_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_category_parent ON category(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_product_category ON product(category_id);
CREATE INDEX IF NOT EXISTS idx_product_brand ON product(brand_id);
CREATE INDEX IF NOT EXISTS idx_product_seller ON product(seller_id);
CREATE INDEX IF NOT EXISTS idx_product_created_at ON product(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_seller ON orders(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_item_order ON order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_order_item_product ON order_item(product_id);
CREATE INDEX IF NOT EXISTS idx_promotion_product_promo ON promotion_product(promotion_id);
CREATE INDEX IF NOT EXISTS idx_promotion_product_product ON promotion_product(product_id);

COMMIT;
"""

TRUNCATE_SQL = """
TRUNCATE TABLE
    promotion_product,
    promotion,
    order_item,
    orders,
    product,
    seller,
    category,
    brand
RESTART IDENTITY CASCADE;
"""


def create_schema(conn: PGConnection) -> None:
    """Create the database schema and indexes required by the seed pipeline."""
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
    conn.commit()


def truncate_seed_tables(conn: PGConnection) -> None:
    """Remove existing seed data and reset identities for a clean reload."""
    with conn.cursor() as cur:
        cur.execute(TRUNCATE_SQL)
    conn.commit()
