-- =========================================
-- ROW COUNTS
-- =========================================

SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM raw.customers

UNION ALL

SELECT 'products', COUNT(*)
FROM raw.products

UNION ALL

SELECT 'orders', COUNT(*)
FROM raw.orders

UNION ALL

SELECT 'order_items', COUNT(*)
FROM raw.order_items

UNION ALL

SELECT 'payments', COUNT(*)
FROM raw.payments

UNION ALL

SELECT 'shipments', COUNT(*)
FROM raw.shipments;


-- =========================================
-- DUPLICATE CHECKS
-- =========================================

SELECT
    customer_id,
    COUNT(*)
FROM raw.customers
GROUP BY customer_id
HAVING COUNT(*) > 1;


SELECT
    order_id,
    COUNT(*)
FROM raw.orders
GROUP BY order_id
HAVING COUNT(*) > 1;


-- =========================================
-- NULL CHECKS
-- =========================================

SELECT COUNT(*) AS null_customer_ids
FROM raw.customers
WHERE customer_id IS NULL;


SELECT COUNT(*) AS null_order_ids
FROM raw.orders
WHERE order_id IS NULL;


SELECT COUNT(*) AS null_product_ids
FROM raw.products
WHERE product_id IS NULL;


-- =========================================
-- RELATIONSHIP CHECKS
-- =========================================

-- Orders without customers

SELECT COUNT(*) AS orphan_orders
FROM raw.orders o
LEFT JOIN raw.customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- Order items without orders

SELECT COUNT(*) AS orphan_order_items
FROM raw.order_items oi
LEFT JOIN raw.orders o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;


-- Order items without products

SELECT COUNT(*) AS orphan_products
FROM raw.order_items oi
LEFT JOIN raw.products p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;


-- Payments without orders

SELECT COUNT(*) AS orphan_payments
FROM raw.payments p
LEFT JOIN raw.orders o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL;


-- Shipments without orders

SELECT COUNT(*) AS orphan_shipments
FROM raw.shipments s
LEFT JOIN raw.orders o
    ON s.order_id = o.order_id
WHERE o.order_id IS NULL;


-- =========================================
-- STATUS DISTRIBUTIONS
-- =========================================

SELECT
    order_status,
    COUNT(*)
FROM raw.orders
GROUP BY order_status
ORDER BY COUNT(*) DESC;


SELECT
    payment_status,
    COUNT(*)
FROM raw.payments
GROUP BY payment_status
ORDER BY COUNT(*) DESC;


SELECT
    shipment_status,
    COUNT(*)
FROM raw.shipments
GROUP BY shipment_status
ORDER BY COUNT(*) DESC;