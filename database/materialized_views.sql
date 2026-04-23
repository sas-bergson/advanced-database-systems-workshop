-- Materialized view: Product sales statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS product_sales_stats AS
SELECT
    p.id AS product_id,
    p.name AS product_name,
    p.price,
    p.stock_quantity,
    c.name AS category_name,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
    COUNT(DISTINCT o.id) AS order_count
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
GROUP BY p.id, p.name, p.price, p.stock_quantity, c.name
WITH DATA;

-- Index on product_sales_stats for fast lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_product_sales_stats_product_id
ON product_sales_stats(product_id);

-- Materialized view: Category sales summary
CREATE MATERIALIZED VIEW IF NOT EXISTS category_sales_summary AS
SELECT
    c.id AS category_id,
    c.name AS category_name,
    COUNT(DISTINCT p.id) AS product_count,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
GROUP BY c.id, c.name
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_category_sales_summary_category_id
ON category_sales_summary(category_id);

-- Function to refresh all materialized views concurrently
CREATE OR REPLACE FUNCTION refresh_sales_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_sales_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY category_sales_summary;
END;
$$ LANGUAGE plpgsql;
