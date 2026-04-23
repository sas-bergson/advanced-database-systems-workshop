# Testing Guide

Comprehensive testing strategies for ShopDB.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
├── test_auth.py         # Authentication tests
├── test_products.py     # Product catalog tests
├── test_orders.py       # Order management tests
├── test_cart.py         # Shopping cart tests
└── test_models.py       # Model tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_products.py
```

### Run Specific Test
```bash
pytest tests/test_products.py::test_list_products
```

### Run with Coverage
```bash
pip install pytest-cov
pytest --cov=app tests/
```

### Run in Watch Mode
```bash
pip install pytest-watch
ptw tests/
```

## Test Fixtures

Common fixtures defined in `conftest.py`:

### app
```python
@pytest.fixture
def app():
    """Create application with testing config."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
```

### client
```python
@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
```

### authenticated_client
```python
@pytest.fixture
def authenticated_client(client, app):
    """Create authenticated test client."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    return client
```

## Test Examples

### Authentication Test
```python
def test_user_registration(client):
    """Test user registration."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm': 'password123'
    })
    assert response.status_code == 302  # Redirect after success
```

### Product Test
```python
def test_list_products(client):
    """Test listing products."""
    response = client.get('/products')
    assert response.status_code == 200
    assert b'Products' in response.data
```

### Cart Test
```python
def test_add_to_cart(authenticated_client, app):
    """Test adding product to cart."""
    with app.app_context():
        product = Product.query.first()
        
        response = authenticated_client.post(f'/cart/add/{product.id}', data={
            'quantity': 2
        })
        
        cart = CartItem.query.first()
        assert cart.quantity == 2
```

## Test Categories

### Unit Tests
- Model methods
- Utility functions
- Individual business logic

### Integration Tests
- Database operations
- Model relationships
- Controller-model interactions

### End-to-End Tests
- User workflows
- Complete request-response cycles
- Multi-step operations

## Best Practices

✅ **Do:**
- Write descriptive test names
- Test both success and failure cases
- Use fixtures for setup/teardown
- Mock external dependencies
- Keep tests focused and isolated
- Use meaningful assertions

❌ **Don't:**
- Use shared test data between tests
- Depend on test execution order
- Make unnecessary network calls
- Test implementation details
- Skip error case testing

## Continuous Integration

Tests run automatically on:
- Pull request creation
- Commits to main branch
- Push to any branch
- Manual workflow trigger

See `.github/workflows/` for CI configuration.

## Next Steps

- [Contributing Guide](contributing.md)
- [Performance Tuning](performance.md)
- [Architecture Overview](../architecture/overview.md)
