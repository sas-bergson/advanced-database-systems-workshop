# Order Model

Order management and order items model.

**Class:** `Order`, `OrderItem`  
**Module:** `app/models/order.py`

## Order

Represents customer orders.

### Database Columns

| Column         | Type          | Description             |
| -------------- | ------------- | ----------------------- |
| `id`           | INTEGER       | Unique order identifier |
| `user_id`      | INTEGER       | Customer reference      |
| `status`       | VARCHAR(20)   | Order status            |
| `total_amount` | NUMERIC(10,2) | Order total price       |
| `created_at`   | TIMESTAMP     | Order creation date     |
| `updated_at`   | TIMESTAMP     | Last update date        |

### Status Values

- `pending` - Awaiting processing
- `confirmed` - Order confirmed
- `shipped` - In transit
- `delivered` - Successfully delivered
- `cancelled` - Order cancelled

### Relationships

- **user**: Order belongs to customer (N:1)
- **order_items**: Order contains line items (1:N)

## OrderItem

Line items within an order.

### Database Columns

| Column       | Type          | Description            |
| ------------ | ------------- | ---------------------- |
| `id`         | INTEGER       | Unique item identifier |
| `order_id`   | INTEGER       | Order reference        |
| `product_id` | INTEGER       | Product reference      |
| `quantity`   | INTEGER       | Item quantity          |
| `unit_price` | NUMERIC(10,2) | Price at purchase      |

### Key Methods

- `get_total()` - Calculate line item total
- `to_dict()` - Convert to dictionary

## Source Code

File: [`app/models/order.py`](../../app/models/order.py)

---

**Auto-generated documentation** - See [DOCUMENTATION.md](../../DOCUMENTATION.md) for details.
