# Cart Model

Shopping cart management model.

**Class:** `CartItem`  
**Module:** `app/models/cart.py`

## Overview

Represents items in user shopping carts.

## Database Columns

| Column       | Type      | Description                 |
| ------------ | --------- | --------------------------- |
| `id`         | INTEGER   | Unique cart item identifier |
| `user_id`    | INTEGER   | Cart owner reference        |
| `product_id` | INTEGER   | Product reference           |
| `quantity`   | INTEGER   | Item quantity               |
| `added_at`   | TIMESTAMP | Addition date               |

## Relationships

- **user**: Cart item belongs to user (N:1)
- **product**: Cart item contains product (N:1)

## Unique Constraint

One product per user's cart (user_id, product_id must be unique)

## Key Methods

- `get_total()` - Calculate line total
- `update_quantity(quantity)` - Update item quantity
- `to_dict()` - Convert to dictionary

## Source Code

File: [`app/models/cart.py`](../../app/models/cart.py)

---

**Auto-generated documentation** - See [DOCUMENTATION.md](../../DOCUMENTATION.md) for details.
