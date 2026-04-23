# Indexing Strategy

Database indexes for optimal query performance.

## Index Overview

Indexes are database structures that improve query performance by providing quick access to data.

## Index Types

### B-Tree Indexes (Default)

Used for equality and range queries.

```sql
-- Create B-Tree index
CREATE INDEX idx_products_price ON products(price);

-- Range query benefit
SELECT * FROM products WHERE price BETWEEN 100 AND 500;
```

### Hash Indexes

Used for exact equality matches.

```sql
-- Create hash index
CREATE INDEX idx_users_email ON users USING HASH(email);

-- Equality query
SELECT * FROM users WHERE email = 'user@example.com';
```

### Composite Indexes

Multiple columns for complex queries.

```sql
-- Create composite index
CREATE INDEX idx_order_items_order_product ON order_items(order_id, product_id);

-- Queries using both columns
SELECT * FROM order_items WHERE order_id = 42 AND product_id = 7;
```

### Partial Indexes

Index only subset of rows.

```sql
-- Only index active products
CREATE INDEX idx_products_active ON products(name) WHERE is_active = TRUE;
```

## Current Indexes

### Foreign Key Indexes

Optimize joins:

```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_cart_items_user ON cart_items(user_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
```

## Query Performance Analysis

### EXPLAIN PLAN

Analyze query performance:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.name, SUM(oi.quantity)
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY SUM(oi.quantity) DESC;
```

Output interpretation:
- **Seq Scan** - Full table scan (potentially slow)
- **Index Scan** - Using index (fast)
- **Buffer** - Memory access information
- **Cost** - Relative execution cost
- **Rows** - Estimated vs actual rows

### Example: Identifying Missing Indexes

```sql
-- Slow query without index
EXPLAIN SELECT * FROM products WHERE stock_quantity < 10;

-- Output shows Seq Scan - add index
CREATE INDEX idx_products_stock ON products(stock_quantity);

-- Rerun EXPLAIN - now uses Index Scan
```

## Monitoring Indexes

### Unused Indexes

Find indexes that aren't being used:

```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Index Sizes

Check index storage:

```sql
SELECT 
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan as scans
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Missing Indexes

Identify frequently scanned tables without appropriate indexes:

```sql
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_scan DESC;
```

## Index Maintenance

### Analyze Table Statistics

```sql
-- Update table statistics for query planner
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;

-- Analyze all tables
ANALYZE;
```

### Rebuild Indexes

```sql
-- Rebuild single index
REINDEX INDEX idx_products_price;

-- Rebuild all table indexes
REINDEX TABLE products;

-- Online rebuild (concurrent)
REINDEX INDEX CONCURRENTLY idx_products_price;
```

### Remove Unused Indexes

```sql
-- Drop unused index
DROP INDEX IF EXISTS idx_unused_index;
```

## Indexing Best Practices

✅ **Create indexes for:**
- Foreign key columns (required for joins)
- Columns in WHERE clauses
- Columns in ORDER BY
- Columns in JOIN conditions
- High-cardinality columns

❌ **Avoid indexing:**
- Low-cardinality columns (gender, status)
- Columns rarely queried
- Small tables
- Text columns (unless full-text search)
- Columns with many NULL values

## Index Recommendations

### High Priority
```sql
-- Foreign keys (enable efficient joins)
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
```

### Medium Priority
```sql
-- Time-based queries
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_created ON products(created_at DESC);

-- Price range queries
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
```

### Performance Monitoring
```sql
-- Identify slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
WHERE mean_time > 100  -- Queries taking > 100ms
ORDER BY mean_time DESC;
```

## Load Test Scenarios

Test index effectiveness under load:

```bash
# Install pgbench
pgbench -i -s 10 shopdb

# Run load test
pgbench -c 10 -j 2 -t 10000 shopdb
```

## Summary

- **Monitor** index usage regularly
- **Remove** unused indexes
- **Create** indexes for join and filter columns
- **Analyze** slow queries with EXPLAIN PLAN
- **Rebuild** indexes during maintenance windows

## Next Steps

- [Materialized Views](materialized-views.md)
- [Stored Procedures](stored-procedures.md)
- [Performance Tuning](../development/performance.md)
