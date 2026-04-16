import pytest
from app.models import db
from app.models.product import Category, Product


def _create_product(app, cat_name='Test Category', name='Test Product',
                    price=29.99, stock=10):
    with app.app_context():
        cat = Category(name=cat_name, description='Test')
        db.session.add(cat)
        db.session.commit()
        product = Product(
            name=name,
            description='A test product description',
            price=price,
            stock_quantity=stock,
            category_id=cat.id,
        )
        db.session.add(product)
        db.session.commit()
        return product.id


class TestProductList:
    def test_list_returns_200(self, client, app):
        _create_product(app)
        response = client.get('/products/')
        assert response.status_code == 200

    def test_list_shows_products(self, client, app):
        _create_product(app, name='Visible Product')
        response = client.get('/products/')
        assert b'Visible Product' in response.data

    def test_list_inactive_products_hidden(self, client, app):
        with app.app_context():
            cat = Category(name='Hidden Cat', description='x')
            db.session.add(cat)
            db.session.commit()
            p = Product(
                name='Hidden Product',
                price=9.99,
                stock_quantity=5,
                category_id=cat.id,
                is_active=False,
            )
            db.session.add(p)
            db.session.commit()
        response = client.get('/products/')
        assert b'Hidden Product' not in response.data

    def test_list_search_finds_matching(self, client, app):
        _create_product(app, cat_name='Search Cat', name='Unique Gamma Widget')
        response = client.get('/products/?search=Gamma')
        assert response.status_code == 200
        assert b'Unique Gamma Widget' in response.data

    def test_list_search_excludes_non_matching(self, client, app):
        _create_product(app, cat_name='Excl Cat', name='Alpha Item')
        response = client.get('/products/?search=Zeta')
        assert b'Alpha Item' not in response.data


class TestProductDetail:
    def test_detail_returns_200(self, client, app):
        pid = _create_product(app, cat_name='Detail Cat', name='Detail Product')
        response = client.get(f'/products/{pid}')
        assert response.status_code == 200

    def test_detail_shows_product_name(self, client, app):
        pid = _create_product(app, cat_name='Info Cat', name='Info Product')
        response = client.get(f'/products/{pid}')
        assert b'Info Product' in response.data

    def test_detail_shows_price(self, client, app):
        pid = _create_product(app, cat_name='Price Cat', name='Priced Item', price=49.99)
        response = client.get(f'/products/{pid}')
        assert b'49.99' in response.data

    def test_detail_404_for_missing(self, client):
        response = client.get('/products/99999')
        assert response.status_code == 404
