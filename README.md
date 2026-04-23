# ShopDB — Advanced Database Systems Workshop

A full-featured E-commerce platform built with **Flask + PostgreSQL** demonstrating advanced database patterns:

- **MVC Design Pattern** — Blueprints as controllers, SQLAlchemy models, Jinja2 templates
- **Stored Procedures** — Atomic order creation via `create_order_from_cart()`, status transitions via `update_order_status()`
- **Materialized Views** — Pre-computed `product_sales_stats` and `category_sales_summary` for fast analytics reporting
- **Asynchronous Polling** — Order detail pages poll `/orders/<id>/status` every 5 seconds for live status updates

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | Flask 2.3 |
| ORM | SQLAlchemy 2.0 + Flask-SQLAlchemy 3.1 |
| Authentication | Flask-Login 0.6 |
| Database | PostgreSQL (production) / SQLite (tests) |
| Frontend | Bootstrap 5 (CDN) |
| Testing | pytest + pytest-flask |

---

## Project Structure

```
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User with password hashing
│   │   ├── product.py       # Category + Product
│   │   ├── order.py         # Order + OrderItem
│   │   └── cart.py          # CartItem
│   ├── controllers/         # Flask Blueprints
│   │   ├── auth.py          # /auth — login, register, logout
│   │   ├── products.py      # /products — list & detail
│   │   ├── orders.py        # /orders — list, detail, create, status poll
│   │   ├── cart.py          # /cart — view, add, update, remove
│   │   └── main.py          # / — home page
│   └── templates/           # Jinja2 templates (Bootstrap 5)
├── static/
│   ├── css/style.css
│   └── js/polling.js        # Async polling implementation
├── database/
│   ├── schema.sql           # Tables + sample data
│   ├── stored_procedures.sql
│   └── materialized_views.sql
├── tests/                   # pytest test suite (SQLite in-memory)
├── config.py                # Dev / Test / Production configs
├── run.py                   # Entry point
└── requirements.txt
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL

```bash
createdb ecommerce_db
psql ecommerce_db < database/schema.sql
psql ecommerce_db < database/stored_procedures.sql
psql ecommerce_db < database/materialized_views.sql
```

### 3. Configure environment

```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://localhost/ecommerce_db"
```

Or create a `.env` file:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://localhost/ecommerce_db
```

### 4. Run the application

```bash
python run.py
```

Visit [http://localhost:5000](http://localhost:5000)

---

## Running Tests

Tests use SQLite in-memory (no PostgreSQL required):

```bash
pytest -v
```

---

## Key Features

### Stored Procedure — Order Creation

`create_order_from_cart(user_id)` atomically:
1. Validates all cart items have sufficient stock
2. Creates the `orders` record
3. Inserts `order_items` rows
4. Decrements `products.stock_quantity`
5. Clears the cart
6. Returns the new order ID

The Flask route tries the stored procedure first and falls back to Python/SQLAlchemy for SQLite compatibility in tests.

### Materialized Views

| View | Purpose |
|------|---------|
| `product_sales_stats` | Units sold, revenue, order count per product |
| `category_sales_summary` | Aggregated sales per category |

Refresh with: `SELECT refresh_sales_stats();`

### Asynchronous Polling

`static/js/polling.js` calls `GET /orders/<id>/status` every 5 seconds.  
When the status changes the badge updates in real-time and a dismissible alert is shown.  
Polling stops automatically when the order reaches `delivered` or `cancelled`.
