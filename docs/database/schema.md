# Database Schema Documentation

Complete reference for the ShopDB PostgreSQL schema.

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │◄──────────────────┐
├─────────────┤                    │
│ id (PK)     │                    │
│ username    │                    │
│ email       │                    │
│ password    │                    │
│ created_at  │                    │
│ is_admin    │                    │
└─────────────┘                    │
      ▲                            │
      │                            │
      │ (1:N)                      │
      │                            │
┌─────┴──────┐          ┌──────────┴──────┐
│   orders   │          │  cart_items     │
├────────────┤          ├─────────────────┤
│ id (PK)    │          │ id (PK)         │
│ user_id    │◄─────────│ user_id (FK)    │
│ status     │          │ product_id(FK)  │
│ total      │          │ quantity        │
│ created_at │          │ added_at        │
│ updated_at │          └─────────────────┘
└─────┬──────┘
      │ (1:N)
      │
┌─────▼──────────┐
│  order_items   │
├────────────────┤
│ id (PK)        │
│ order_id (FK)  │
│ product_id(FK) │
│ quantity       │
│ unit_price     │
└────────────────┘
      ▲
      │
      │ (N:1)
      │
┌─────┴──────────┐
│   products     │
├────────────────┤
│ id (PK)        │
│ name           │
│ description    │
│ price          │
│ stock_qty      │
│ category_id    │
│ image_url      │
│ created_at     │
│ is_active      │
└────────────────┘
      ▲
      │ (N:1)
      │
┌─────┴──────────┐
│  categories    │
├────────────────┤
│ id (PK)        │
│ name           │
│ description    │
└────────────────┘
```

## Tables

### users

**Purpose:** Store user account information with authentication data.

| Column          | Type         | Constraints     | Description           |
| --------------- | ------------ | --------------- | --------------------- |
| `id`            | SERIAL       | PRIMARY KEY     | Unique identifier     |
| `username`      | VARCHAR(80)  | UNIQUE NOT NULL | Login username        |
| `email`         | VARCHAR(120) | UNIQUE NOT NULL | User email address    |
| `password_hash` | VARCHAR(256) | NOT NULL        | Bcrypt password hash  |
| `created_at`    | TIMESTAMP    | DEFAULT NOW()   | Account creation time |
| `is_admin`      | BOOLEAN      | DEFAULT FALSE   | Administrator flag    |

**Indexes:**
```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

---

### categories

**Purpose:** Product categorization for organization and filtering.

| Column        | Type         | Constraints     | Description          |
| ------------- | ------------ | --------------- | -------------------- |
| `id`          | SERIAL       | PRIMARY KEY     | Unique identifier    |
| `name`        | VARCHAR(100) | UNIQUE NOT NULL | Category name        |
| `description` | TEXT         | -               | Category description |

**Indexes:**
```sql
CREATE INDEX idx_categories_name ON categories(name);
```

---

### products

**Purpose:** Core product catalog with inventory tracking.

| Column           | Type          | Constraints     | Description       |
| ---------------- | ------------- | --------------- | ----------------- |
| `id`             | SERIAL        | PRIMARY KEY     | Unique identifier |
| `name`           | VARCHAR(200)  | NOT NULL        | Product name      |
| `description`    | TEXT          | -               | Product details   |
| `price`          | NUMERIC(10,2) | NOT NULL        | Product price     |
| `stock_quantity` | INTEGER       | DEFAULT 0       | Available stock   |
| `category_id`    | INTEGER       | FK → categories | Product category  |
| `image_url`      | VARCHAR(500)  | -               | Product image URL |
| `created_at`     | TIMESTAMP     | DEFAULT NOW()   | Creation time     |
| `is_active`      | BOOLEAN       | DEFAULT TRUE    | Active status     |

**Indexes:**
```sql
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_price ON products(price);
```

---

### orders

**Purpose:** Purchase orders with status tracking.

| Column         | Type          | Constraints       | Description       |
| -------------- | ------------- | ----------------- | ----------------- |
| `id`           | SERIAL        | PRIMARY KEY       | Unique identifier |
| `user_id`      | INTEGER       | FK → users        | Order creator     |
| `status`       | VARCHAR(20)   | DEFAULT 'pending' | Order status      |
| `total_amount` | NUMERIC(10,2) | -                 | Order total       |
| `created_at`   | TIMESTAMP     | DEFAULT NOW()     | Creation time     |
| `updated_at`   | TIMESTAMP     | DEFAULT NOW()     | Last update       |

**Valid Status Values:**
- `pending` - Awaiting processing
- `confirmed` - Order confirmed
- `shipped` - In transit
- `delivered` - Successfully delivered
- `cancelled` - Order cancelled

**Indexes:**
```sql
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
```

---

### order_items

**Purpose:** Line items in orders with pricing snapshot.

| Column       | Type          | Constraints   | Description       |
| ------------ | ------------- | ------------- | ----------------- |
| `id`         | SERIAL        | PRIMARY KEY   | Unique identifier |
| `order_id`   | INTEGER       | FK → orders   | Associated order  |
| `product_id` | INTEGER       | FK → products | Product ordered   |
| `quantity`   | INTEGER       | NOT NULL      | Order quantity    |
| `unit_price` | NUMERIC(10,2) | NOT NULL      | Price at purchase |

**Indexes:**
```sql
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

---

### cart_items

**Purpose:** Temporary shopping cart data.

| Column       | Type      | Constraints   | Description       |
| ------------ | --------- | ------------- | ----------------- |
| `id`         | SERIAL    | PRIMARY KEY   | Unique identifier |
| `user_id`    | INTEGER   | FK → users    | Cart owner        |
| `product_id` | INTEGER   | FK → products | Product in cart   |
| `quantity`   | INTEGER   | DEFAULT 1     | Item quantity     |
| `added_at`   | TIMESTAMP | DEFAULT NOW() | Addition time     |

**Constraints:**
- UNIQUE(user_id, product_id) - One entry per product per user

**Indexes:**
```sql
CREATE INDEX idx_cart_items_user ON cart_items(user_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
```

## Key Relationships

### 1:N Relationships

- **users → orders** - One user has many orders
- **users → cart_items** - One user has one cart with many items
- **orders → order_items** - One order has many line items
- **categories → products** - One category has many products
- **products → order_items** - One product appears in many orders
- **products → cart_items** - One product in many shopping carts

### Unique Constraints

- `users.username` - Prevent duplicate usernames
- `users.email` - Prevent duplicate emails
- `categories.name` - Prevent duplicate categories
- `cart_items(user_id, product_id)` - One product per cart per user

## Referential Integrity

All foreign keys use:
- **ON DELETE:** CASCADE (dependent records removed)
- **ON UPDATE:** CASCADE (changes propagated)

## Performance Considerations

1. **Indexes on Foreign Keys** - Enable efficient joins
2. **Indexes on Queries** - Support filtering and sorting
3. **Composite Indexes** - Optimize multi-column queries
4. **Partial Indexes** - Filter for active records

## Sample Data

The schema includes sample data:
- **8 products** across 4 categories
- **Pre-configured categories** for easy browsing

See [schema.sql](../../database/schema.sql) for complete initialization.

## Next Steps

- [Stored Procedures](stored-procedures.md)
- [Materialized Views](materialized-views.md)
- [Indexing Strategy](indexing.md)
