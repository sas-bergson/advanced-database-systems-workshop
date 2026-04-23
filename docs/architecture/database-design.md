# Database Design Principles

Principles and patterns used in ShopDB database design.

## Normalization

ShopDB uses 3rd Normal Form (3NF) to reduce redundancy and ensure data integrity.

### 1NF - Atomic Values
All values are atomic (indivisible):

```sql
-- ❌ Bad - Non-atomic
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    product_ids VARCHAR  -- Multiple values!
);

-- ✅ Good - Atomic
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER
);
```

### 2NF - No Partial Dependencies
All non-key attributes depend on the entire primary key:

```sql
-- ❌ Bad - Partial dependency
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    product_name VARCHAR,  -- Depends only on product_id, not both keys!
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);

-- ✅ Good - Separated tables
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);
```

### 3NF - No Transitive Dependencies
No non-key attribute depends on another non-key attribute:

```sql
-- ❌ Bad - Transitive dependency
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    category_name VARCHAR,
    category_description VARCHAR  -- Depends on category_name, not product_id
);

-- ✅ Good - Separated tables
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    description VARCHAR
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id)
);
```

## Entity Integrity

Every table has a primary key:

```sql
-- ✅ Every table has primary key
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- Unique identifier
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL
);
```

## Referential Integrity

Foreign keys maintain consistency between tables:

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id)
);
```

## Domain Integrity

Data types enforce valid values:

```sql
-- ✅ Proper data types
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,          -- Text
    price NUMERIC(10, 2) NOT NULL,       -- Money
    stock_quantity INTEGER DEFAULT 0,    -- Count
    created_at TIMESTAMP DEFAULT NOW(),  -- Date/time
    is_active BOOLEAN DEFAULT TRUE       -- Flag
);

-- ✅ Check constraints
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered')),
    total_amount NUMERIC(10, 2) CHECK (total_amount >= 0)
);
```

## Relationships

### One-to-Many
One category has many products:

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id)
);
```

### One-to-One
One user has one profile:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80)
);

CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    bio TEXT
);
```

### Many-to-Many
Many students take many courses:

```sql
-- ❌ Bad - Direct many-to-many relationship
-- Can't have both foreign keys as primary key if multiple enrollments

-- ✅ Good - Junction table
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    UNIQUE(student_id, course_id)
);
```

## Indexing Strategy

```sql
-- Indexes for common queries
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- Indexes for uniqueness
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

## Transaction Control

Ensure ACID properties:

```sql
BEGIN TRANSACTION;

-- Related operations
INSERT INTO orders (...) VALUES (...);
UPDATE products SET stock_quantity = stock_quantity - 1;

COMMIT;  -- All or nothing
```

## Backup & Recovery

### Full Backup
```bash
pg_dump shopdb > backup_full.sql
```

### Incremental Backup
```bash
# Use WAL files for point-in-time recovery
```

### Recovery
```bash
psql shopdb < backup_full.sql
```

## Performance Optimization

1. **Indexing** - Speed up common queries
2. **Denormalization** - When needed for performance
3. **Materialized Views** - Pre-computed results
4. **Partitioning** - Divide large tables
5. **Connection Pooling** - Reuse connections

## Anti-patterns to Avoid

### ❌ Surrogate Keys Everywhere
```sql
-- Unnecessary surrogate key
CREATE TABLE category_names (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR UNIQUE
);
```

### ❌ Over-normalization
```sql
-- Too many joins needed
CREATE TABLE numbers (
    id INTEGER PRIMARY KEY,
    value INTEGER
);
```

### ❌ Redundant Data
```sql
-- Duplicate data violates normalization
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR,  -- Duplicate from users table!
    user_email VARCHAR  -- Another duplicate!
);
```

## Design Checklist

- [ ] All tables have primary keys
- [ ] No duplicate data between tables
- [ ] Foreign keys reference correct tables
- [ ] Data types are appropriate
- [ ] Check constraints validate data
- [ ] Indexes on frequently queried columns
- [ ] Proper normalization level (3NF)
- [ ] Relationships clearly defined

## Next Steps

- [Schema Documentation](../database/schema.md)
- [Indexing Strategy](../database/indexing.md)
- [MVC Pattern](mvc-pattern.md)
