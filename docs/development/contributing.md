# Contributing Guide

How to contribute to ShopDB development.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/advanced-database-systems-workshop.git
cd advanced-database-systems-workshop
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions

### 3. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development Workflow

### Running the Application

```bash
export FLASK_ENV=development
export DATABASE_URL="postgresql://shopuser:password@localhost:5432/shopdb"
python run.py
```

### Running Tests

```bash
pytest tests/ -v
pytest tests/test_products.py -v
pytest --cov=app tests/
```

### Code Style

Follow PEP 8:

```bash
pip install flake8 black autopep8

# Check style
flake8 app/

# Auto-format
black app/
autopep8 --in-place --aggressive --aggressive app/
```

### Type Hints

Add type hints to functions:

```python
from typing import List, Optional
from app.models.product import Product

def get_products(limit: int = 10) -> List[Product]:
    """Fetch products with limit."""
    return Product.query.limit(limit).all()
```

## Making Changes

### Code Changes

1. **Understand the feature** - Read related documentation
2. **Write tests first** - TDD approach
3. **Implement feature** - Write clean, readable code
4. **Run tests** - Ensure all tests pass
5. **Update docs** - Document changes

### Database Changes

1. **Schema changes** - Update `database/schema.sql`
2. **Procedures** - Update `database/stored_procedures.sql`
3. **Views** - Update `database/materialized_views.sql`
4. **Tests** - Add migration tests

### Documentation Changes

1. **API docs** - Update endpoint descriptions
2. **Model docs** - Document new fields
3. **README** - Update setup instructions
4. **Examples** - Add usage examples

## Testing Requirements

### Unit Tests
```python
def test_product_creation(app):
    """Test creating a product."""
    with app.app_context():
        product = Product(name="Test", price=9.99, stock_quantity=10)
        db.session.add(product)
        db.session.commit()
        
        assert product.id is not None
        assert product.name == "Test"
```

### Integration Tests
```python
def test_add_to_cart_flow(client, app):
    """Test complete add-to-cart flow."""
    # Setup
    with app.app_context():
        product = Product.query.first()
    
    # Act
    response = client.post(f'/cart/add/{product.id}', data={'quantity': 1})
    
    # Assert
    assert response.status_code == 302
```

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style
- `refactor:` - Code refactoring
- `test:` - Test addition
- `perf:` - Performance improvement

### Examples

```bash
git commit -m "feat: add product filtering by category"
git commit -m "fix: resolve cart item quantity bug"
git commit -m "docs: add API documentation"
git commit -m "refactor: simplify order validation logic"
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code follows style guide
3. ✅ Documentation updated
4. ✅ Commits are descriptive
5. ✅ No merge conflicts
6. ✅ Branch is up to date with main

### PR Template

```markdown
## Description
What does this PR do?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Breaking change

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code style checked
- [ ] No breaking changes
```

### Review Process

1. Maintainer reviews code
2. Feedback provided if needed
3. Changes requested or approved
4. Merging to main branch
5. Deployment and monitoring

## Reporting Bugs

### Bug Report Template

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Linux/macOS/Windows
- Python: 3.8/3.9/3.10/3.11
- PostgreSQL: 12/13/14/15

## Additional Context
Screenshots, logs, etc.
```

## Feature Requests

### Feature Request Template

```markdown
## Description
What feature would you like?

## Use Case
Why do you need this?

## Proposed Solution
How should it work?

## Alternatives Considered
Other ways to solve this

## Additional Context
Related features, designs, etc.
```

## Questions?

- Check existing documentation
- Search closed issues
- Open a discussion
- Contact maintainers

## Code of Conduct

### Expected Behavior
- Be respectful and inclusive
- Welcome different perspectives
- Provide constructive feedback
- Focus on the code, not the person

### Unacceptable Behavior
- Harassment or discrimination
- Insulting or demeaning language
- Unwelcome sexual advances
- Doxxing or sharing private info

---

**Thank you for contributing! 🎉**
