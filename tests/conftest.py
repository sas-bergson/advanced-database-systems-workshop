import pytest
from app import create_app
from app.models import db


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def register_user(client, username='testuser', email='test@test.com', password='testpass123'):
    return client.post('/auth/register', data={
        'username': username,
        'email': email,
        'password': password,
    }, follow_redirects=True)


def login_user(client, username='testuser', password='testpass123'):
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)
