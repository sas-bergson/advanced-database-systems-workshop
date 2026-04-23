# Materialized Views Documentation

Pre-computed data for fast analytics queries.

## Overview

Materialized views are database objects that store pre-computed query results. Unlike regular views, they persist the data to disk and require explicit refresh, enabling fast analytics queries.

## product_sales_stats

**Purpose:** Pre-computed sales statistics by product.

### View Definition

```sql
CREATE MATERIALIZED VIEW product_sales_stats AS
SELECT 
    p.id,
    p.name,
    p.price,
    COUNT(DISTINCT oi.order_id) as total_orders,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.quantity * oi.unit_price) as total_revenue,
    AVG(oi.unit_price) as average_price,
    MAX(o.created_at) as last_sale_date,
    p.stock_quantity
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id
GROUP BY p.id, p.name, p.price, p.stock_quantity;

CREATE INDEX idx_product_sales_stats_revenue ON product_sales_stats(total_revenue DESC);
```

### Columns

| Column                | Type      | Description           |
| --------------------- | --------- | --------------------- |
| `id`                  | INTEGER   | Product ID            |
| `name`                | VARCHAR   | Product name          |
| `price`               | NUMERIC   | Current price         |
| `total_orders`        | BIGINT    | Number of orders      |
| `total_quantity_sold` | BIGINT    | Total units sold      |
| `total_revenue`       | NUMERIC   | Total sales revenue   |
| `average_price`       | NUMERIC   | Average selling price |
| `last_sale_date`      | TIMESTAMP | Most recent sale      |
| `stock_quantity`      | INTEGER   | Current stock         |

### Example Queries

#### Top 10 Best Sellers
```sql
SELECT 
    id, name, total_revenue, total_quantity_sold
FROM product_sales_stats
ORDER BY total_revenue DESC
LIMIT 10;
```

#### Low Stock Alert
```sql
SELECT 
    id, name, stock_quantity, total_orders
FROM product_sales_stats
WHERE stock_quantity < 20
ORDER BY stock_quantity ASC;
```

#### Sales Trend
```sql
SELECT 
    name, 
    total_revenue,
    (total_revenue::NUMERIC / total_orders) as avg_order_value
FROM product_sales_stats
ORDER BY total_revenue DESC;
```

---

## category_sales_summary

**Purpose:** Aggregated sales metrics by product category.

### View Definition

```sql
CREATE MATERIALIZED VIEW category_sales_summary AS
SELECT 
    c.id,
    c.name,
    COUNT(DISTINCT p.id) as product_count,
    COUNT(DISTINCT oi.order_id) as total_orders,
    SUM(oi.quantity) as total_units_sold,
    SUM(oi.quantity * oi.unit_price) as total_revenue,
    AVG(oi.unit_price) as average_unit_price,
    MIN(p.price) as min_price,
    MAX(p.price) as max_price,
    MAX(o.created_at) as last_order_date
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id
GROUP BY c.id, c.name;

CREATE INDEX idx_category_sales_revenue ON category_sales_summary(total_revenue DESC);
```

### Columns

| Column               | Type      | Description        |
| -------------------- | --------- | ------------------ |
| `id`                 | INTEGER   | Category ID        |
| `name`               | VARCHAR   | Category name      |
| `product_count`      | BIGINT    | Number of products |
| `total_orders`       | BIGINT    | Number of orders   |
| `total_units_sold`   | BIGINT    | Units sold         |
| `total_revenue`      | NUMERIC   | Category revenue   |
| `average_unit_price` | NUMERIC   | Average price      |
| `min_price`          | NUMERIC   | Lowest price       |
| `max_price`          | NUMERIC   | Highest price      |
| `last_order_date`    | TIMESTAMP | Recent activity    |

### Example Queries

#### Category Performance Ranking
```sql
SELECT 
    name,
    product_count,
    total_orders,
    total_revenue,
    ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (), 2) as revenue_percentage
FROM category_sales_summary
ORDER BY total_revenue DESC;
```

#### Price Range Analysis
```sql
SELECT 
    name,
    min_price,
    max_price,
    (max_price - min_price) as price_range,
    average_unit_price
FROM category_sales_summary
ORDER BY price_range DESC;
```

---

## Refresh Strategy

### Manual Refresh

```sql
-- Refresh single view
REFRESH MATERIALIZED VIEW product_sales_stats;
REFRESH MATERIALIZED VIEW category_sales_summary;

-- Refresh all views
REFRESH MATERIALIZED VIEW product_sales_stats;
REFRESH MATERIALIZED VIEW category_sales_summary;
```

### Concurrent Refresh (non-blocking)

```sql
-- Allows queries while refreshing (PostgreSQL 9.5+)
REFRESH MATERIALIZED VIEW CONCURRENTLY product_sales_stats;
```

### Automated Refresh Schedule

Create a maintenance function:

```sql
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Refreshing materialized views...';
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_sales_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY category_sales_summary;
    RAISE NOTICE 'Materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;
```

Schedule with pg_cron:

```sql
-- Refresh every hour
SELECT cron.schedule('refresh-materialized-views', '0 * * * *', 'SELECT refresh_materialized_views()');
```

---

## Performance Impact

### Benefits
- ⚡ **Fast Analytics** - Pre-computed results
- 📊 **Complex Aggregations** - Expensive calculations pre-done
- 🔍 **Real-time Dashboards** - Quick data retrieval
- 💾 **Reduced CPU Load** - No expensive joins at query time

### Trade-offs
- 📈 **Storage** - Extra disk space for computed data
- 🔄 **Staleness** - Data is only as fresh as last refresh
- 🛠️ **Maintenance** - Requires refresh scheduling

### Size Estimate

```sql
-- Check materialized view sizes
SELECT 
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
FROM pg_matviews
ORDER BY pg_total_relation_size(schemaname||'.'||matviewname) DESC;
```

---

## Monitoring

### View Freshness

```sql
-- Query to track last refresh
SELECT 
    schemaname,
    matviewname,
    (SELECT MAX(updated_at) FROM orders) as last_data_change
FROM pg_matviews
WHERE schemaname = 'public';
```

### Query Performance

```sql
-- Slow query log
SELECT 
    query,
    calls,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE query LIKE '%product_sales_stats%'
ORDER BY mean_time DESC;
```

## Next Steps

- [Indexing Strategy](indexing.md)
- [Stored Procedures](stored-procedures.md)
- [Database Schema](schema.md)
