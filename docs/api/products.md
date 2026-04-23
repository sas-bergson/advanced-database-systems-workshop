# Products API

Product catalog and browsing endpoints.

## List Products

Retrieve all products with pagination and filtering.

**Endpoint:** `GET /products`

**Parameters:**
- `page` (integer) - Page number (default: 1)
- `category` (integer) - Filter by category ID
- `min_price` (decimal) - Minimum price filter
- `max_price` (decimal) - Maximum price filter
- `search` (string) - Search products by name

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Laptop Pro 15",
      "price": 1299.99,
      "category_id": 1,
      "stock_quantity": 50,
      "image_url": "https://...",
      "is_active": true
    }
  ],
  "total": 42,
  "pages": 3,
  "current_page": 1
}
```

## Get Product Details

Retrieve detailed information about a specific product.

**Endpoint:** `GET /products/<id>`

**Parameters:**
- `id` (integer) - Product ID

**Response:**
```json
{
  "id": 1,
  "name": "Laptop Pro 15",
  "description": "High-performance laptop...",
  "price": 1299.99,
  "category": {
    "id": 1,
    "name": "Electronics"
  },
  "stock_quantity": 50,
  "image_url": "https://...",
  "is_active": true,
  "created_at": "2024-04-23T10:30:00"
}
```

**Status Codes:**
- `200` - Product found
- `404` - Product not found

## Get Product as JSON

Get product data for API consumption.

**Endpoint:** `GET /products/<id>/api`

**Response:** Same as Get Product Details

---

**Auto-generated documentation** - See [DOCUMENTATION.md](../../DOCUMENTATION.md) for details.
