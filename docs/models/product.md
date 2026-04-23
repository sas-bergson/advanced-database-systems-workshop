# Product Model

Product catalog and inventory management model.

**Class:** `Product`  
**Module:** `app/models/product.py`

## Overview

Represents products in the catalog with inventory tracking.

## Database Columns

| Column           | Type          | Description               |
| ---------------- | ------------- | ------------------------- |
| `id`             | INTEGER       | Unique product identifier |
| `name`           | VARCHAR(200)  | Product name              |
| `description`    | TEXT          | Detailed description      |
| `price`          | NUMERIC(10,2) | Product price             |
| `stock_quantity` | INTEGER       | Available inventory       |
| `category_id`    | INTEGER       | Category reference        |
| `image_url`      | VARCHAR(500)  | Product image URL         |
| `created_at`     | TIMESTAMP     | Creation date             |
| `is_active`      | BOOLEAN       | Active status flag        |

## Relationships

- **category**: Product belongs to category (N:1)
- **order_items**: Product appears in orders (N:M)
- **cart_items**: Product in shopping carts (N:M)

## Key Methods

- `is_in_stock()` - Check if product has inventory
- `to_dict()` - Convert to dictionary
- `reduce_stock(quantity)` - Decrease inventory
- `increase_stock(quantity)` - Increase inventory

## Source Code

File: [`app/models/product.py`](../../app/models/product.py)

---

**Auto-generated documentation** - See [DOCUMENTATION.md](../../DOCUMENTATION.md) for details.
