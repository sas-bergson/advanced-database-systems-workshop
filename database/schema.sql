-- Drop and recreate tables
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS product_attributes CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS attributes CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS customer_tiers CASCADE;
DROP TABLE IF EXISTS exchange_rates CASCADE;
DROP TABLE IF EXISTS currencies CASCADE;


-- Create currencies table
CREATE TABLE currencies (
currency_code CHAR (3) PRIMARY KEY ,
currency_name VARCHAR (50) NOT NULL ,
symbol VARCHAR (10)
);

-- Create exchange-rates table
CREATE TABLE exchange_rates (
    exchange_rate_id SERIAL PRIMARY KEY,
    from_currency_code CHAR(3) NOT NULL REFERENCES currencies(currency_code),
    to_currency_code CHAR(3) NOT NULL REFERENCES currencies(currency_code),
    rate NUMERIC(18, 8) NOT NULL CHECK (rate > 0),
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (from_currency_code <> to_currency_code),
    CHECK (valid_to IS NULL OR valid_to > valid_from),
    UNIQUE (from_currency_code, to_currency_code, valid_from)
);

-- Create customer-tiers table
CREATE TABLE customer_tiers (
    tier_id INT PRIMARY KEY ,
    tier_name VARCHAR (20) NOT NULL ,
    discount_percentage DECIMAL (5,2) CHECK (discount_percentage BETWEEN 0 AND 100),
    min_lifetime_value DECIMAL (12 ,2) DEFAULT 0
);

-- Create warehouse table
CREATE TABLE warehouses (
warehouse_id INT PRIMARY KEY ,
location VARCHAR (100) NOT NULL ,
capacity INT
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    tier_id INT REFERENCES customer_tiers (tier_id ),
    lifetime_value DECIMAL (12 ,2) DEFAULT 0.0 ,
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]+$')
);

-- Create categories table
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Create products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price NUMERIC(10, 2) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    image_url VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
    CHECK (image_url IS NULL OR image_url ~* '^https?://[^[:space:]]+$')
);

-- Create attributes table
CREATE TABLE attributes (
    attribute_id INT PRIMARY KEY ,
    attribute _name VARCHAR (50) NOT NULL
);

-- relationship between attributes table and products table
CREATE TABLE product_attributes (
    product_id INT REFERENCES products (product_id),
    attribute_id INT REFERENCES attributes (attribute_id),
    value VARCHAR (100) NOT NULL ,
    PRIMARY KEY (product_id, attribute_id)
);

-- relationship between products table and the wharehouses table
CREATE TABLE Inventory (
    inventory_id INT PRIMARY KEY,
    product_id INT REFERENCES products (product_id),
    warehouse_id INT REFERENCES warehouses (warehouse_id),
    quantity_on_hand INT DEFAULT 0 ,
    reorder_threshold INT DEFAULT 10 ,
    UNIQUE (product_id, warehouse_id)
);

-- Create orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) NOT NULL,
    product_id INTEGER REFERENCES products(product_id) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

-- Create cart_items table
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    product_id INTEGER REFERENCES products(product_id) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Currencies
INSERT INTO currencies (currency_code, currency_name, symbol) VALUES
    ('USD', 'US Dollar',          '$'),
    ('EUR', 'Euro',               '€'),
    ('GBP', 'British Pound',      '£'),
    ('JPY', 'Japanese Yen',       '¥'),
    ('CAD', 'Canadian Dollar',    'C$'),
    ('AUD', 'Australian Dollar',  'A$');

-- Exchange rates (as of seed date)
INSERT INTO exchange_rates (from_currency_code, to_currency_code, rate, valid_from) VALUES
    ('USD', 'EUR', 0.92340000, '2026-01-01 00:00:00'),
    ('USD', 'GBP', 0.79120000, '2026-01-01 00:00:00'),
    ('USD', 'JPY', 149.87000000, '2026-01-01 00:00:00'),
    ('USD', 'CAD', 1.36450000, '2026-01-01 00:00:00'),
    ('USD', 'AUD', 1.53210000, '2026-01-01 00:00:00'),
    ('EUR', 'GBP', 0.85680000, '2026-01-01 00:00:00'),
    ('EUR', 'JPY', 162.30000000, '2026-01-01 00:00:00'),
    ('EUR', 'USD', 1.08300000, '2026-01-01 00:00:00'),
    ('GBP', 'USD', 1.26390000, '2026-01-01 00:00:00'),
    ('CAD', 'USD', 0.73290000, '2026-01-01 00:00:00');

-- Customer tiers
INSERT INTO customer_tiers (tier_id, tier_name, discount_percentage, min_lifetime_value) VALUES
    (1, 'Bronze',   0.00,   0.00),
    (2, 'Silver',   5.00,   500.00),
    (3, 'Gold',     10.00,  2000.00),
    (4, 'Platinum', 15.00,  5000.00);

-- Warehouses (minimum 5)
INSERT INTO warehouses (warehouse_id, location, capacity) VALUES
    (1, 'New York, NY',      50000),
    (2, 'Los Angeles, CA',   60000),
    (3, 'Chicago, IL',       45000),
    (4, 'Houston, TX',       55000),
    (5, 'Phoenix, AZ',       40000),
    (6, 'Philadelphia, PA',  35000),
    (7, 'San Antonio, TX',   30000);

-- Categories
INSERT INTO categories (name, description) VALUES
    ('Electronics',    'Electronic devices and accessories'),
    ('Clothing',       'Apparel and fashion items'),
    ('Books',          'Books and educational materials'),
    ('Home & Garden',  'Home decor and garden supplies');

-- Users (50 users; user 1 is admin; tiers cycle 1-4)
INSERT INTO users (username, email, password_hash, is_admin, tier_id, lifetime_value)
SELECT
    'user' || i,
    'user' || i || '@example.com',
    md5('secret' || i),
    (i = 1),
    (((i - 1) % 4) + 1),
    ROUND((i * 213.75)::NUMERIC, 2)
FROM generate_series(1, 50) AS s(i);

-- Products (30 products across 4 categories)
INSERT INTO products (name, description, base_price, category_id, image_url) VALUES
    -- Electronics (category 1)
    ('Laptop Pro 15',       'High-performance laptop, 16GB RAM, 512GB SSD',   1299.99, 1, 'https://via.placeholder.com/300x200?text=Laptop'),
    ('Wireless Headphones', 'Noise-cancelling Bluetooth headphones',            199.99, 1, 'https://via.placeholder.com/300x200?text=Headphones'),
    ('Smart Watch',         'Fitness tracker with heart rate monitor',          299.99, 1, 'https://via.placeholder.com/300x200?text=SmartWatch'),
    ('4K Monitor 27"',      'IPS panel, 144Hz, HDR400',                         449.99, 1, 'https://via.placeholder.com/300x200?text=Monitor'),
    ('Mechanical Keyboard', 'TKL layout, Cherry MX Red switches',               129.99, 1, 'https://via.placeholder.com/300x200?text=Keyboard'),
    ('Gaming Mouse',        'Optical 16000 DPI wireless gaming mouse',           79.99, 1, 'https://via.placeholder.com/300x200?text=Mouse'),
    ('USB-C Hub 7-in-1',    'HDMI, USB-A x3, SD, MicroSD, PD 100W',             49.99, 1, 'https://via.placeholder.com/300x200?text=Hub'),
    ('Portable SSD 1TB',    'NVMe USB-C, up to 1050 MB/s read',                109.99, 1, 'https://via.placeholder.com/300x200?text=SSD'),
    -- Clothing (category 2)
    ('Running Shoes',       'Lightweight and durable running shoes',             89.99, 2, 'https://via.placeholder.com/300x200?text=Shoes'),
    ('Classic T-Shirt',     '100% cotton, pre-shrunk, unisex',                  19.99, 2, 'https://via.placeholder.com/300x200?text=TShirt'),
    ('Slim Fit Jeans',      'Stretch denim, five-pocket style',                 59.99, 2, 'https://via.placeholder.com/300x200?text=Jeans'),
    ('Waterproof Jacket',   'Breathable membrane, taped seams',                 149.99, 2, 'https://via.placeholder.com/300x200?text=Jacket'),
    ('Wool Sweater',        'Merino wool, ribbed cuffs and hem',                 99.99, 2, 'https://via.placeholder.com/300x200?text=Sweater'),
    ('Sports Shorts',       'Quick-dry fabric, 7" inseam',                      34.99, 2, 'https://via.placeholder.com/300x200?text=Shorts'),
    ('Leather Belt',        'Full-grain leather, nickel buckle',                 39.99, 2, 'https://via.placeholder.com/300x200?text=Belt'),
    -- Books (category 3)
    ('Python Programming Book',      'Complete guide to Python 3',              49.99, 3, 'https://via.placeholder.com/300x200?text=Python+Book'),
    ('Database Systems Book',        'Advanced database systems textbook',       79.99, 3, 'https://via.placeholder.com/300x200?text=DB+Book'),
    ('Data Structures & Algorithms', 'Problem-solving with DSA in Python',       59.99, 3, 'https://via.placeholder.com/300x200?text=DSA+Book'),
    ('Machine Learning Handbook',    'End-to-end ML workflows with scikit-learn',69.99, 3, 'https://via.placeholder.com/300x200?text=ML+Book'),
    ('Clean Code',                   'A handbook of agile software craftsmanship',44.99, 3, 'https://via.placeholder.com/300x200?text=CleanCode'),
    ('Design Patterns',              'Elements of reusable OO software',         54.99, 3, 'https://via.placeholder.com/300x200?text=DesignPatterns'),
    ('The Pragmatic Programmer',     '20th anniversary edition',                 49.99, 3, 'https://via.placeholder.com/300x200?text=PragProg'),
    -- Home & Garden (category 4)
    ('Yoga Mat',          'Non-slip, 6mm eco-friendly TPE',                      35.99, 4, 'https://via.placeholder.com/300x200?text=YogaMat'),
    ('Coffee Maker',      'Programmable 12-cup with thermal carafe',             59.99, 4, 'https://via.placeholder.com/300x200?text=CoffeeMaker'),
    ('Air Purifier',      'HEPA H13, covers 500 sq ft, quiet mode',             129.99, 4, 'https://via.placeholder.com/300x200?text=AirPurifier'),
    ('Smart Thermostat',  'Wi-Fi, 7-day scheduling, energy reports',            179.99, 4, 'https://via.placeholder.com/300x200?text=Thermostat'),
    ('Garden Hose 50ft',  'Expandable, kink-free, brass fittings',               29.99, 4, 'https://via.placeholder.com/300x200?text=GardenHose'),
    ('Electric Kettle',   '1.7 L, 1500W, keep-warm function',                   39.99, 4, 'https://via.placeholder.com/300x200?text=Kettle'),
    ('Robot Vacuum',      'LiDAR mapping, 3000 Pa suction, app control',        349.99, 4, 'https://via.placeholder.com/300x200?text=RobotVacuum'),
    ('Standing Desk',     'Electric height-adjustable, 60"x24" top',            499.99, 4, 'https://via.placeholder.com/300x200?text=StandingDesk');

-- Attributes
INSERT INTO attributes (attribute_id) VALUES (1),(2),(3),(4),(5);

-- Product attributes (all 30 products x 5 attributes)
-- attribute 1=Color, 2=Size, 3=Weight, 4=Material, 5=Brand
INSERT INTO product_attributes (product_id, attribute_id, value)
SELECT
    p,
    a,
    CASE a
        WHEN 1 THEN (ARRAY['Black','Silver','White','Blue','Red'])[(p % 5) + 1]
        WHEN 2 THEN (ARRAY['Small','Medium','Large','XL','XXL'])[(p % 5) + 1]
        WHEN 3 THEN (ROUND((0.3 + p * 0.4)::NUMERIC, 1)::TEXT || ' kg')
        WHEN 4 THEN (ARRAY['Plastic','Metal','Fabric','Wood','Glass'])[(p % 5) + 1]
        WHEN 5 THEN (ARRAY['BrandA','BrandB','BrandC','BrandD','BrandE'])[(p % 5) + 1]
    END
FROM generate_series(1, 30) AS sp(p),
     generate_series(1, 5)  AS sa(a);

-- Inventory (30 products x 7 warehouses)
INSERT INTO inventory (inventory_id, product_id, warehouse_id, quantity_on_hand, reorder_threshold)
SELECT
    (w - 1) * 30 + p,
    p,
    w,
    ((p * w * 17) % 491) + 10,
    5 + (p % 10) * 3
FROM generate_series(1, 30) AS sp(p),
     generate_series(1, 7)  AS sw(w);

-- Orders (100 orders; users cycle 1-50; status cycles through lifecycle)
INSERT INTO orders (user_id, status, total_amount, created_at, updated_at)
SELECT
    ((i - 1) % 50) + 1,
    (ARRAY['pending','processing','shipped','delivered','cancelled'])[(i % 5) + 1],
    0.00,
    CURRENT_TIMESTAMP - ((100 - i) || ' days')::INTERVAL,
    CURRENT_TIMESTAMP - ((100 - i) || ' days')::INTERVAL + '2 hours'::INTERVAL
FROM generate_series(1, 100) AS s(i);

-- Order items (12 items per order = 1200 rows)
-- Prime step (13) over 30 products guarantees 12 distinct product_ids per order.
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT
    o.order_id,
    ((o.order_id * 13 + item.j) % 30) + 1,
    (item.j % 5) + 1,
    p.base_price
FROM orders o
CROSS JOIN generate_series(0, 11) AS item(j)
JOIN products p ON p.product_id = ((o.order_id * 13 + item.j) % 30) + 1;

-- Update order total_amount from order_items
UPDATE orders o
SET total_amount = (
    SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
    FROM order_items oi
    WHERE oi.order_id = o.order_id
);

-- Cart items (50 users x 24 products = 1200 rows; UNIQUE(user_id,product_id) safe)
INSERT INTO cart_items (user_id, product_id, quantity, added_at)
SELECT
    ((s.i - 1) / 24) + 1,
    ((s.i - 1) % 24) + 1,
    ((s.i % 5) + 1),
    CURRENT_TIMESTAMP - (((s.i % 30) + 1) || ' days')::INTERVAL
FROM generate_series(1, 1200) AS s(i);
