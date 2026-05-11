SELECT COUNT(*) AS brands FROM brand;
SELECT COUNT(*) AS categories FROM category;
SELECT COUNT(*) AS sellers FROM seller;
SELECT COUNT(*) AS products FROM product;
SELECT COUNT(*) AS promotions FROM promotion;
SELECT COUNT(*) AS promotion_products FROM promotion_product;
SELECT COUNT(*) AS orders FROM orders;
SELECT COUNT(*) AS order_items FROM order_item;

SELECT COUNT(*) AS bad_discount_rows
FROM product
WHERE discount_price > price;

SELECT COUNT(*) AS bad_category_hierarchy_rows
FROM category child
LEFT JOIN category parent ON child.parent_category_id = parent.category_id
WHERE
    (child.level = 1 AND child.parent_category_id IS NOT NULL)
    OR (child.level = 2 AND child.parent_category_id IS NULL)
    OR (child.level = 2 AND parent.level <> 1);

SELECT COUNT(*) AS missing_fk_products
FROM product p
LEFT JOIN brand b ON p.brand_id = b.brand_id
LEFT JOIN category c ON p.category_id = c.category_id
LEFT JOIN seller s ON p.seller_id = s.seller_id
WHERE b.brand_id IS NULL OR c.category_id IS NULL OR s.seller_id IS NULL;

SELECT COUNT(*) AS missing_fk_orders
FROM orders o
LEFT JOIN seller s ON o.seller_id = s.seller_id
WHERE s.seller_id IS NULL;

SELECT COUNT(*) AS missing_fk_order_items
FROM order_item oi
LEFT JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN product p ON oi.product_id = p.product_id
WHERE o.order_id IS NULL OR p.product_id IS NULL;

SELECT COUNT(*) AS bad_order_item_subtotals
FROM order_item
WHERE subtotal <> quantity * unit_price;

SELECT COUNT(*) AS bad_order_totals
FROM orders o
JOIN (
    SELECT order_id, SUM(subtotal) AS item_total
    FROM order_item
    GROUP BY order_id
) oi ON o.order_id = oi.order_id
WHERE o.total_amount <> oi.item_total;

SELECT COUNT(*) AS missing_fk_promotion_products
FROM promotion_product pp
LEFT JOIN promotion pr ON pp.promotion_id = pr.promotion_id
LEFT JOIN product p ON pp.product_id = p.product_id
WHERE pr.promotion_id IS NULL OR p.product_id IS NULL;

SELECT COUNT(*) AS duplicate_promotion_product_pairs
FROM (
    SELECT promotion_id, product_id
    FROM promotion_product
    GROUP BY promotion_id, product_id
    HAVING COUNT(*) > 1
) duplicate_pairs;

SELECT COUNT(*) AS bad_promotion_date_ranges
FROM promotion
WHERE end_date < start_date;
