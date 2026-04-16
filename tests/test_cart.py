import json
import pytest
from app.models import db
from app.models.product import Category, Product
from app.models.cart import CartItem
from app.models.user import User
from tests.conftest import register_user, login_user


def _setup_product(app, cat_name='Cart Cat', prod_name='Cart Product',
                   price=25.00, stock=10):
    with app.app_context():
        cat = Category(name=cat_name, description='Test')
        db.session.add(cat)
        db.session.commit()
        product = Product(
            name=prod_name,
            description='For cart testing',
            price=price,
            stock_quantity=stock,
            category_id=cat.id,
        )
        db.session.add(product)
        db.session.commit()
        return product.id


class TestCartView:
    def test_cart_requires_login(self, client):
        response = client.get('/cart/', follow_redirects=False)
        assert response.status_code == 302

    def test_cart_view_empty(self, client):
        register_user(client)
        login_user(client)
        response = client.get('/cart/')
        assert response.status_code == 200
        assert b'empty' in response.data


class TestAddToCart:
    def test_add_to_cart_success(self, client, app):
        product_id = _setup_product(app)
        register_user(client)
        login_user(client)
        response = client.post('/cart/add',
                               data=json.dumps({'product_id': product_id, 'quantity': 2}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['cart_count'] == 1

    def test_add_to_cart_requires_login(self, client, app):
        product_id = _setup_product(app, cat_name='Auth Cat')
        response = client.post('/cart/add',
                               data=json.dumps({'product_id': product_id, 'quantity': 1}),
                               content_type='application/json',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_add_nonexistent_product(self, client):
        register_user(client)
        login_user(client)
        response = client.post('/cart/add',
                               data=json.dumps({'product_id': 99999, 'quantity': 1}),
                               content_type='application/json')
        assert response.status_code == 404

    def test_add_exceeds_stock(self, client, app):
        product_id = _setup_product(app, cat_name='Stock Cat', stock=3)
        register_user(client)
        login_user(client)
        response = client.post('/cart/add',
                               data=json.dumps({'product_id': product_id, 'quantity': 100}),
                               content_type='application/json')
        assert response.status_code == 400

    def test_add_same_product_increments_quantity(self, client, app):
        product_id = _setup_product(app, cat_name='Incr Cat', stock=20)
        register_user(client)
        login_user(client)
        client.post('/cart/add',
                    data=json.dumps({'product_id': product_id, 'quantity': 1}),
                    content_type='application/json')
        client.post('/cart/add',
                    data=json.dumps({'product_id': product_id, 'quantity': 2}),
                    content_type='application/json')
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            item = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()
            assert item.quantity == 3


class TestUpdateCart:
    def test_update_cart_quantity(self, client, app):
        product_id = _setup_product(app, cat_name='Upd Cat')
        register_user(client)
        login_user(client)
        client.post('/cart/add',
                    data=json.dumps({'product_id': product_id, 'quantity': 1}),
                    content_type='application/json')
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            item = CartItem.query.filter_by(user_id=user.id).first()
            item_id = item.id

        response = client.post('/cart/update',
                               data=json.dumps({'item_id': item_id, 'quantity': 5}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_update_cart_zero_removes_item(self, client, app):
        product_id = _setup_product(app, cat_name='Zero Cat')
        register_user(client)
        login_user(client)
        client.post('/cart/add',
                    data=json.dumps({'product_id': product_id, 'quantity': 1}),
                    content_type='application/json')
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            item = CartItem.query.filter_by(user_id=user.id).first()
            item_id = item.id

        client.post('/cart/update',
                    data=json.dumps({'item_id': item_id, 'quantity': 0}),
                    content_type='application/json')
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            remaining = CartItem.query.filter_by(user_id=user.id).all()
            assert len(remaining) == 0


class TestRemoveFromCart:
    def test_remove_cart_item(self, client, app):
        product_id = _setup_product(app, cat_name='Rm Cat')
        register_user(client)
        login_user(client)
        client.post('/cart/add',
                    data=json.dumps({'product_id': product_id, 'quantity': 1}),
                    content_type='application/json')
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            item = CartItem.query.filter_by(user_id=user.id).first()
            item_id = item.id

        response = client.post('/cart/remove',
                               data=json.dumps({'item_id': item_id}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            remaining = CartItem.query.filter_by(user_id=user.id).all()
            assert len(remaining) == 0

    def test_remove_nonexistent_item(self, client):
        register_user(client)
        login_user(client)
        response = client.post('/cart/remove',
                               data=json.dumps({'item_id': 99999}),
                               content_type='application/json')
        assert response.status_code == 404
