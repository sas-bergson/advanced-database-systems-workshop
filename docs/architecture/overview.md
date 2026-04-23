# Architecture Overview

Complete system design and design patterns used in ShopDB.

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Client Layer                            │
│              (Browser / JavaScript / HTML)                 │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ HTTP/HTTPS
                     │
┌────────────────────▼─────────────────────────────────────┐
│                  Flask Application                        │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Blueprints (Controllers)              │  │
│  │  • auth.py   - Authentication & Authorization     │  │
│  │  • products.py - Product catalog & browsing       │  │
│  │  • orders.py   - Order management & history       │  │
│  │  • cart.py     - Shopping cart operations         │  │
│  │  • main.py     - Home & general routes            │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                SQLAlchemy ORM Layer                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Models (Data Mapping)                 │  │
│  │  • User - User accounts & authentication          │  │
│  │  • Product - Product catalog                      │  │
│  │  • Order - Order records & items                  │  │
│  │  • CartItem - Shopping cart items                 │  │
│  └────────────────────────────────────────────────────┘  │
│  • Query Building & Validation                           │
│  • Relationship Management                               │
│  • Transaction Control                                   │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ SQL Queries
                     │
┌────────────────────▼─────────────────────────────────────┐
│              PostgreSQL Database                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Schema (Tables & Constraints)             │  │
│  │  • users, categories, products, orders, etc.      │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │       Stored Procedures & Functions               │  │
│  │  • create_order_from_cart()                       │  │
│  │  • update_order_status()                          │  │
│  │  • recalculate_materialized_views()               │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │       Materialized Views (Analytics)              │  │
│  │  • product_sales_stats                            │  │
│  │  • category_sales_summary                         │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │       Indexes (Performance)                       │  │
│  │  • Foreign key indexes for joins                  │  │
│  │  • Query optimization indexes                     │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. MVC (Model-View-Controller)

**Models** (`app/models/`)
- SQLAlchemy ORM classes
- Business logic & validation
- Database relationships

**Views** (`app/templates/`)
- Jinja2 templates
- HTML markup & styling
- Form rendering

**Controllers** (`app/controllers/`)
- Flask Blueprints
- Route handlers
- Request processing

### 2. Blueprint Pattern

Modular Flask application structure:

```python
# Blueprint Definition
blueprint = Blueprint('products', __name__, url_prefix='/products')

@blueprint.route('/', methods=['GET'])
def list_products():
    products = Product.query.all()
    return render_template('products/list.html', products=products)

# Blueprint Registration
app.register_blueprint(blueprint)
```

### 3. ORM Mapping Pattern

SQLAlchemy handles object-relational mapping:

```python
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Relationships
    orders = db.relationship('Order', backref='user')
    cart_items = db.relationship('CartItem', backref='user')
```

### 4. Active Record Pattern

Models handle their own persistence:

```python
# Create
user = User(username='john', email='john@example.com')
db.session.add(user)
db.session.commit()

# Read
user = User.query.filter_by(username='john').first()

# Update
user.email = 'newemail@example.com'
db.session.commit()

# Delete
db.session.delete(user)
db.session.commit()
```

### 5. Repository Pattern (via SQLAlchemy)

Abstraction of data access:

```python
class UserRepository:
    @staticmethod
    def find_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def create(username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
```

### 6. Template Method Pattern

Base template for common HTML structure:

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}ShopDB{% endblock %}</title>
</head>
<body>
    <nav>{% include 'nav.html' %}</nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>{% include 'footer.html' %}</footer>
</body>
</html>
```

## Request-Response Flow

```
1. Client Request (HTTP)
   ↓
2. Flask Routing (URL → Blueprint)
   ↓
3. Controller/Handler Execution
   ├─ Parse Request Data
   ├─ Validate Input
   ├─ Business Logic
   └─ Model Queries
   ↓
4. Database Operations (SQLAlchemy)
   ├─ Build SQL Query
   ├─ Execute Query
   └─ Fetch Results
   ↓
5. Template Rendering (Jinja2)
   ├─ Load Template
   ├─ Inject Data
   └─ Generate HTML
   ↓
6. Response (HTTP)
   └─ Return to Client
```

## Component Responsibilities

### Controllers (Routes)

- **Request handling** - Parse and validate input
- **Route definition** - Map URLs to handlers
- **Response building** - Prepare output format
- **Error handling** - Catch and handle exceptions

### Models (Data)

- **Data validation** - Enforce business rules
- **Database mapping** - Map objects to tables
- **Relationships** - Define entity associations
- **Query methods** - Implement queries (optional)

### Templates (Presentation)

- **HTML structure** - Semantic markup
- **Data display** - Render model data
- **Forms** - Collect user input
- **Navigation** - Provide UI flow

### Database (Persistence)

- **Data storage** - Persistent record keeping
- **ACID properties** - Data consistency
- **Transactions** - Multi-step operations
- **Analytics** - Aggregated insights

## Data Flow Examples

### Create Order from Cart

```
1. User clicks "Checkout"
   ↓
2. POST /orders/create (cart_id)
   ↓
3. OrdersController.create_from_cart()
   ├─ Validate user session
   ├─ Verify cart ownership
   └─ Call create_order_from_cart() procedure
   ↓
4. PostgreSQL Procedure
   ├─ Lock inventory
   ├─ Create order record
   ├─ Copy cart items → order_items
   ├─ Update stock
   └─ Clear cart
   ↓
5. Return order details
   ↓
6. Render order confirmation page
   ↓
7. Response to browser
```

### List Products with Filtering

```
1. GET /products?category=electronics&min_price=100
   ↓
2. ProductsController.list()
   ├─ Extract filters
   ├─ Build ORM query
   │  Product.query
   │    .filter_by(category_id=1)
   │    .filter(Product.price >= 100)
   │    .all()
   └─ Prepare for rendering
   ↓
3. SQLAlchemy → SQL Query
   SELECT * FROM products 
   WHERE category_id = 1 
   AND price >= 100
   ↓
4. PostgreSQL execution
   ├─ Use indexes if available
   └─ Return result set
   ↓
5. Render products/list.html
   └─ Loop through products, display each
   ↓
6. Response to browser (HTML)
```

## Scalability Considerations

### Horizontal Scaling
- **Application**: Stateless Flask instances behind load balancer
- **Database**: Read replicas with master-slave replication
- **Cache**: Redis for session & query result caching

### Vertical Scaling
- **Connection pooling**: SQLAlchemy connection pooling
- **Query optimization**: Indexes, query analysis
- **Materialized views**: Pre-computed expensive queries

### Performance Optimization
- **Lazy loading**: Load relationships on demand
- **Eager loading**: Load relationships upfront when known
- **Database indexes**: Speed up frequent queries
- **Caching**: Cache expensive computations

## Next Steps

- [MVC Pattern Details](mvc-pattern.md)
- [Database Design Principles](database-design.md)
- [Performance Tuning](../development/performance.md)
