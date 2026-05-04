SELECT COUNT(*) AS brands FROM brand;
SELECT COUNT(*) AS categories FROM category;
SELECT COUNT(*) AS sellers FROM seller;
SELECT COUNT(*) AS products FROM product;
SELECT COUNT(*) AS promotions FROM promotion;
SELECT COUNT(*) AS promotion_products FROM promotion_product;

SELECT COUNT(*) AS bad_discount_rows
FROM product
WHERE discount_price > price;

SELECT COUNT(*) AS missing_fk_products
FROM product p
LEFT JOIN brand b ON p.brand_id = b.brand_id
LEFT JOIN category c ON p.category_id = c.category_id
LEFT JOIN seller s ON p.seller_id = s.seller_id
WHERE b.brand_id IS NULL OR c.category_id IS NULL OR s.seller_id IS NULL;
