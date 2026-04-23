# Performance Tuning Guide

Optimize ShopDB for production performance.

## Database Performance

### Query Optimization

#### Use EXPLAIN ANALYZE
```sql
EXPLAIN ANALYZE
SELECT p.name, COUNT(*) as order_count
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name;
```

#### Connection Pooling
```python
# app/__init__.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'max_overflow': 40,
    'pool_pre_ping': True,
}
```

#### Query Caching
```python
from functools import wraps
from flask import cache

@cache.cached(timeout=300, key_prefix='products_list')
def get_all_products():
    return Product.query.all()
```

### Index Optimization

```sql
-- Check missing indexes
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_scan DESC;
```

### Connection Limits

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Set max connections
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

## Application Performance

### Lazy Loading vs Eager Loading

```python
# Lazy Loading (Multiple queries)
orders = Order.query.all()
for order in orders:
    print(order.user.username)  # N+1 queries!

# Eager Loading (Single query with JOIN)
orders = Order.query.options(
    joinedload(Order.user)
).all()
```

### Pagination

```python
def list_products(page: int = 1, per_page: int = 20):
    pagination = Product.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
    }
```

### Batch Operations

```python
# Slow - Individual inserts
for product_data in products:
    product = Product(**product_data)
    db.session.add(product)
    db.session.commit()

# Fast - Batch insert
products_list = [Product(**data) for data in products]
db.session.bulk_insert_mappings(Product, products)
db.session.commit()
```

## Caching Strategy

### Fragment Caching

```python
from flask import cache

@cache.cached(timeout=300)
def get_product_summary(product_id: int):
    product = Product.query.get(product_id)
    return {
        'name': product.name,
        'price': product.price,
        'stock': product.stock_quantity
    }
```

### Cache Invalidation

```python
@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    product.name = request.json['name']
    db.session.commit()
    
    # Invalidate cache
    cache.delete_memoized(get_product_summary, id)
    
    return jsonify(product.to_dict())
```

## Monitoring

### Performance Metrics

```python
import time
from functools import wraps

def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f"{f.__name__} took {end-start:.4f}s")
        return result
    return wrapper

@timing
def expensive_operation():
    return Product.query.all()
```

### Slow Query Log

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 second
SELECT pg_reload_conf();

-- View slow queries
tail -f /var/log/postgresql/postgresql.log
```

### Application Profiling

```bash
pip install werkzeug py-spy

# Profile Flask app
py-spy record -o profile.svg -- python run.py
```

## Load Testing

### Using Apache Bench

```bash
# Install ab
sudo apt-get install apache2-utils

# Load test endpoint
ab -n 1000 -c 10 http://localhost:5000/products

# Results show:
# - Requests per second
# - Mean response time
# - Failed requests
```

### Using wrk

```bash
# Install wrk
brew install wrk

# 4 threads, 100 connections, 30 second test
wrk -t4 -c100 -d30s http://localhost:5000/products
```

## Production Optimizations

### 1. Enable Compression

```python
from flask_compress import Compress

Compress(app)
```

### 2. Use Minification

```python
# CSS minification
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.min.css') }}">

# JS minification
<script src="{{ url_for('static', filename='js/script.min.js') }}"></script>
```

### 3. Browser Caching

```python
@app.after_request
def set_cache_headers(response):
    response.cache_control.max_age = 3600  # 1 hour
    response.cache_control.public = True
    return response
```

### 4. Database Connection Pool

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'max_overflow': 40,
    'pool_pre_ping': True,
}
```

### 5. Async Tasks

```python
from celery import Celery

celery = Celery(app.name)
celery.conf.update(app.config)

@celery.task
def send_order_confirmation(order_id):
    order = Order.query.get(order_id)
    # Send email async
```

## Benchmarking Checklist

- [ ] Query response times < 500ms
- [ ] Page load time < 2 seconds
- [ ] Database connections stable
- [ ] Memory usage within limits
- [ ] CPU usage < 80%
- [ ] No N+1 queries
- [ ] Indexes used effectively
- [ ] Cache hit rates > 80%

## Next Steps

- [Testing Guide](testing.md)
- [Contributing Guide](contributing.md)
- [Database Indexing](../database/indexing.md)
