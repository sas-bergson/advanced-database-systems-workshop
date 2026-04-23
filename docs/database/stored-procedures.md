# Stored Procedures Documentation

Advanced database functions for atomic operations and business logic.

## Overview

Stored procedures encapsulate complex SQL operations, ensuring data consistency and providing a security boundary between application and database.

## create_order_from_cart()

**Purpose:** Atomically convert shopping cart to order with inventory updates.

### Signature
```sql
CREATE OR REPLACE FUNCTION create_order_from_cart(
    p_user_id INTEGER
) RETURNS TABLE (
    order_id INTEGER,
    status VARCHAR,
    total_amount NUMERIC,
    items_count INTEGER
)
```

### Parameters

| Parameter   | Type    | Description             |
| ----------- | ------- | ----------------------- |
| `p_user_id` | INTEGER | User ID owning the cart |

### Return Values

| Column         | Type    | Description                     |
| -------------- | ------- | ------------------------------- |
| `order_id`     | INTEGER | Created order ID                |
| `status`       | VARCHAR | Order status (always 'pending') |
| `total_amount` | NUMERIC | Order total                     |
| `items_count`  | INTEGER | Number of line items            |

### Logic

```
1. Validate user exists
2. Verify cart has items
3. Lock inventory rows (FOR UPDATE)
4. Validate stock availability
5. Create order record
6. Copy cart items to order_items
7. Update product inventory
8. Clear user's cart
9. Return order details
10. Commit or rollback atomically
```

### Example Usage

```sql
-- Create order from cart
SELECT * FROM create_order_from_cart(42);

-- Result:
--  order_id | status  | total_amount | items_count
-- ----------+---------+--------------+-------------
--       101 | pending |      1599.97 |           3
```

### Error Handling

| Error                | Cause                         |
| -------------------- | ----------------------------- |
| `USER_NOT_FOUND`     | User ID doesn't exist         |
| `EMPTY_CART`         | Cart has no items             |
| `INSUFFICIENT_STOCK` | Product stock is insufficient |
| `CART_UPDATE_FAILED` | Failed to clear cart          |

---

## update_order_status()

**Purpose:** Safely transition order status with validation.

### Signature
```sql
CREATE OR REPLACE FUNCTION update_order_status(
    p_order_id INTEGER,
    p_new_status VARCHAR
) RETURNS TABLE (
    order_id INTEGER,
    previous_status VARCHAR,
    new_status VARCHAR,
    updated_at TIMESTAMP
)
```

### Parameters

| Parameter      | Type    | Description     |
| -------------- | ------- | --------------- |
| `p_order_id`   | INTEGER | Order to update |
| `p_new_status` | VARCHAR | Target status   |

### Return Values

| Column            | Type      | Description      |
| ----------------- | --------- | ---------------- |
| `order_id`        | INTEGER   | Updated order ID |
| `previous_status` | VARCHAR   | Previous status  |
| `new_status`      | VARCHAR   | New status       |
| `updated_at`      | TIMESTAMP | Update timestamp |

### Valid Transitions

```
pending → confirmed
pending → cancelled
confirmed → shipped
confirmed → cancelled
shipped → delivered
```

### Example Usage

```sql
-- Update order status
SELECT * FROM update_order_status(101, 'confirmed');

-- Result:
--  order_id | previous_status | new_status | updated_at
-- ----------+-----------------+------------+---------------------
--       101 | pending         | confirmed  | 2024-04-23 12:34:56
```

---

## get_user_order_summary()

**Purpose:** Retrieve aggregated order statistics for a user.

### Signature
```sql
CREATE OR REPLACE FUNCTION get_user_order_summary(
    p_user_id INTEGER
) RETURNS TABLE (
    total_orders INTEGER,
    total_spent NUMERIC,
    average_order_value NUMERIC,
    last_order_date TIMESTAMP
)
```

### Example Usage

```sql
SELECT * FROM get_user_order_summary(42);

-- Result:
--  total_orders | total_spent | average_order_value | last_order_date
-- --------------+-------------+---------------------+---------------------
--             5 |    7499.95  |          1499.99    | 2024-04-20 15:30:00
```

---

## recalculate_materialized_views()

**Purpose:** Refresh all materialized views with latest data.

### Signature
```sql
CREATE OR REPLACE FUNCTION recalculate_materialized_views()
RETURNS TABLE (
    view_name VARCHAR,
    rows_updated INTEGER,
    execution_time_ms NUMERIC
)
```

### Example Usage

```sql
-- Refresh all materialized views
SELECT * FROM recalculate_materialized_views();

-- Result:
--            view_name            | rows_updated | execution_time_ms
-- --------------------------------+--------------+-------------------
--  product_sales_stats            |           42 |              125
--  category_sales_summary          |            4 |               45
```

---

## Performance Considerations

### Row-Level Locking
```sql
-- Prevents concurrent modifications
SELECT * FROM products 
WHERE id IN (SELECT product_id FROM cart_items WHERE user_id = $1)
FOR UPDATE;
```

### Transaction Isolation
- **ISOLATION LEVEL:** SERIALIZABLE
- **ENSURES:** No dirty reads, phantom reads, or lost updates

### Index Usage
```sql
-- These indexes support procedure execution
CREATE INDEX idx_cart_items_user ON cart_items(user_id);
CREATE INDEX idx_products_id ON products(id);
CREATE INDEX idx_orders_user ON orders(user_id);
```

## Monitoring Procedures

Monitor procedure execution:

```sql
-- Check slow procedures
SELECT 
    calls,
    total_time,
    mean_time,
    query
FROM pg_stat_statements
WHERE query LIKE '%create_order_from_cart%'
ORDER BY mean_time DESC;
```

## Next Steps

- [Materialized Views](materialized-views.md)
- [Indexing Strategy](indexing.md)
- [Database Schema](schema.md)
