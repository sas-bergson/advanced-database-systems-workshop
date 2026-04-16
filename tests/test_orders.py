import json
import pytest
from app.models import db
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Category, Product
from tests.conftest import register_user, login_user


def _create_order_for_user(app, username, email):
    with app.app_context():
        user = User(username=username, email=email)
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        order = Order(user_id=user.id, status='pending', total_amount=75.00)
        db.session.add(order)
        db.session.commit()
        return user.id, order.id


class TestOrdersList:
    def test_orders_list_requires_login(self, client):
        response = client.get('/orders/', follow_redirects=False)
        assert response.status_code == 302

    def test_orders_list_authenticated_returns_200(self, client):
        register_user(client)
        login_user(client)
        response = client.get('/orders/')
        assert response.status_code == 200

    def test_orders_list_shows_order(self, client, app):
        register_user(client)
        login_user(client)
        # Create an order via the Python-level model (bypasses stored procedure)
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            order = Order(user_id=user.id, status='processing', total_amount=42.00)
            db.session.add(order)
            db.session.commit()
        response = client.get('/orders/')
        assert response.status_code == 200


class TestOrderDetail:
    def test_order_detail_requires_login(self, client, app):
        _, order_id = _create_order_for_user(app, 'detailuser', 'detail@example.com')
        response = client.get(f'/orders/{order_id}', follow_redirects=False)
        assert response.status_code == 302

    def test_order_detail_own_order(self, client, app):
        register_user(client)
        login_user(client)
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            order = Order(user_id=user.id, status='pending', total_amount=10.00)
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        response = client.get(f'/orders/{order_id}')
        assert response.status_code == 200

    def test_order_detail_denied_for_other_user(self, client, app):
        _, order_id = _create_order_for_user(app, 'otheruser', 'other@example.com')
        register_user(client)
        login_user(client)
        response = client.get(f'/orders/{order_id}', follow_redirects=True)
        assert b'Access denied' in response.data

    def test_order_detail_404_for_missing(self, client):
        register_user(client)
        login_user(client)
        response = client.get('/orders/99999')
        assert response.status_code == 404


class TestOrderStatusPolling:
    def test_status_endpoint_returns_json(self, client, app):
        register_user(client)
        login_user(client)
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            order = Order(user_id=user.id, status='pending', total_amount=20.00)
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        response = client.get(f'/orders/{order_id}/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['order_id'] == order_id
        assert data['status'] == 'pending'
        assert 'updated_at' in data

    def test_status_endpoint_requires_login(self, client, app):
        _, order_id = _create_order_for_user(app, 'polluser', 'poll@example.com')
        response = client.get(f'/orders/{order_id}/status', follow_redirects=False)
        assert response.status_code == 302

    def test_status_endpoint_denied_for_other_user(self, client, app):
        _, order_id = _create_order_for_user(app, 'owned', 'owned@example.com')
        register_user(client)
        login_user(client)
        response = client.get(f'/orders/{order_id}/status')
        assert response.status_code == 403
