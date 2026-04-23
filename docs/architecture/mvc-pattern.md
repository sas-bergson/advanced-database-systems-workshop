# MVC Pattern Implementation

Model-View-Controller architecture in ShopDB.

## Pattern Overview

MVC separates an application into three interconnected components:

```
┌─────────────────────────────────────────┐
│   Models (Data Layer)                   │
│  ├─ SQLAlchemy ORM classes              │
│  ├─ Database relationships              │
│  └─ Business logic & validation         │
└─────────────────────────────────────────┘
            ▲              │
            │              │ Query
            │              ▼
┌─────────────────────────────────────────┐
│   Controllers (Logic Layer)             │
│  ├─ Flask Blueprints                    │
│  ├─ Route handlers                      │
│  └─ Request processing                  │
└─────────────────────────────────────────┘
            ▲              │
            │              │ Data
            │              ▼
┌─────────────────────────────────────────┐
│   Views (Presentation Layer)            │
│  ├─ Jinja2 templates                    │
│  ├─ HTML & CSS                          │
│  └─ User interface                      │
└─────────────────────────────────────────┘
```

## Models (Data Layer)

### Purpose
- Represent database entities
- Define relationships
- Implement business logic
- Provide data persistence

### Example: Product Model

```python
# app/models/product.py
from app import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    category = db.relationship('Category', backref='products')
    order_items = db.relationship('OrderItem', backref='product')
    cart_items = db.relationship('CartItem', backref='product')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'stock_quantity': self.stock_quantity,
        }
    
    def is_in_stock(self):
        """Check if product has stock."""
        return self.stock_quantity > 0
```

## Controllers (Logic Layer)

### Purpose
- Handle HTTP requests
- Validate input
- Call model methods
- Return responses

### Example: Products Controller

```python
# app/controllers/products.py
from flask import Blueprint, render_template, request, jsonify
from app.models.product import Product

blueprint = Blueprint('products', __name__, url_prefix='/products')

@blueprint.route('/', methods=['GET'])
def list_products():
    """List all products with pagination."""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    pagination = query.paginate(page=page, per_page=20)
    
    return render_template('products/list.html',
                          products=pagination.items,
                          pagination=pagination)

@blueprint.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details."""
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@blueprint.route('/<int:product_id>/api', methods=['GET'])
def get_product_json(product_id):
    """Get product as JSON."""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())
```

## Views (Presentation Layer)

### Purpose
- Display user interface
- Render data in templates
- Handle client-side interactions
- Provide navigation

### Example: Product List Template

```html
<!-- app/templates/products/list.html -->
{% extends 'base.html' %}

{% block title %}Products - ShopDB{% endblock %}

{% block content %}
<div class="container py-4">
    <h1>Products</h1>
    
    <div class="row">
        {% for product in products %}
        <div class="col-md-4 mb-3">
            <div class="card">
                {% if product.image_url %}
                <img src="{{ product.image_url }}" class="card-img-top" alt="{{ product.name }}">
                {% endif %}
                
                <div class="card-body">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="card-text">{{ product.description[:100] }}...</p>
                    
                    <div class="d-flex justify-content-between">
                        <span class="h5">${{ product.price }}</span>
                        <small class="text-muted">
                            {% if product.is_in_stock() %}
                            In Stock ({{ product.stock_quantity }})
                            {% else %}
                            Out of Stock
                            {% endif %}
                        </small>
                    </div>
                </div>
                
                <div class="card-footer">
                    <a href="{{ url_for('products.get_product', product_id=product.id) }}"
                       class="btn btn-primary btn-sm">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Pagination -->
    {% if pagination.pages > 1 %}
    <nav class="mt-4">
        <ul class="pagination justify-content-center">
            {% if pagination.has_prev %}
            <li class="page-item">
                <a class="page-link" href="{{ url_for('products.list_products', page=pagination.prev_num) }}">
                    Previous
                </a>
            </li>
            {% endif %}
            
            {% for page_num in pagination.iter_pages() %}
            {% if page_num %}
            <li class="page-item {% if page_num == pagination.page %}active{% endif %}">
                <a class="page-link" href="{{ url_for('products.list_products', page=page_num) }}">
                    {{ page_num }}
                </a>
            </li>
            {% endif %}
            {% endfor %}
            
            {% if pagination.has_next %}
            <li class="page-item">
                <a class="page-link" href="{{ url_for('products.list_products', page=pagination.next_num) }}">
                    Next
                </a>
            </li>
            {% endif %}
        </ul>
    </nav>
    {% endif %}
</div>
{% endblock %}
```

## Data Flow

### Create Product Flow

```
1. User submits form (View)
   ↓
2. POST /products/create (Controller)
   - Validate input
   - Check permissions
   ↓
3. Create Product instance (Model)
   - Add validation
   - Set defaults
   ↓
4. Save to database
   - db.session.add(product)
   - db.session.commit()
   ↓
5. Return response (Controller)
   - Redirect or JSON response
```

### Update Product Flow

```
1. User updates form (View)
   ↓
2. PUT /products/<id> (Controller)
   - Validate input
   - Check permissions
   ↓
3. Fetch existing Product (Model)
   - product = Product.query.get_or_404(id)
   ↓
4. Update attributes
   - product.name = request.json['name']
   - product.price = request.json['price']
   ↓
5. Commit changes
   - db.session.commit()
   ↓
6. Return updated product
   - jsonify(product.to_dict())
```

## Best Practices

### ✅ Models
- Keep business logic in models
- Validate data before persistence
- Use meaningful property names
- Implement `__repr__` for debugging
- Use relationships for associations

### ✅ Controllers
- Keep controllers thin
- Delegate logic to models
- Validate all input
- Handle errors gracefully
- Return appropriate HTTP status codes

### ✅ Views
- Keep templates simple
- Minimize logic in templates
- Use template inheritance
- Cache static assets
- Use semantic HTML

## Anti-patterns to Avoid

### ❌ Fat Controllers
```python
# Bad - Too much logic in controller
@blueprint.route('/products', methods=['POST'])
def create_product():
    # Validation
    if not request.json['name']:
        return error_response('Name required')
    
    # Business logic
    category = Category.query.filter_by(...)
    # ... more logic ...
    
    # Database operations
    product = Product(...)
    db.session.add(product)
    db.session.commit()
```

### ✅ Better - Delegate to Models
```python
# Good - Thin controller, logic in model
@blueprint.route('/products', methods=['POST'])
def create_product():
    product = Product.from_json(request.json)
    product.save()
    return jsonify(product.to_dict()), 201
```

## Next Steps

- [Architecture Overview](overview.md)
- [Database Design](database-design.md)
- [Testing Guide](../development/testing.md)
