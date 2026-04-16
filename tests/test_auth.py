import pytest
from tests.conftest import register_user, login_user


class TestRegistration:
    def test_register_success(self, client):
        response = register_user(client)
        assert response.status_code == 200
        assert b'Registration successful' in response.data

    def test_register_duplicate_username(self, client):
        register_user(client)
        response = register_user(client, email='other@example.com')
        assert b'Username already exists' in response.data

    def test_register_duplicate_email(self, client):
        register_user(client)
        response = register_user(client, username='otheruser')
        assert b'Email already registered' in response.data

    def test_register_redirects_to_login(self, client):
        # After successful registration, user is redirected to login page
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'pass123',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']


class TestLogin:
    def test_login_success(self, client):
        register_user(client)
        response = login_user(client)
        assert response.status_code == 200
        assert b'Login successful' in response.data

    def test_login_wrong_password(self, client):
        register_user(client)
        response = login_user(client, password='wrongpassword')
        assert b'Invalid username or password' in response.data

    def test_login_unknown_user(self, client):
        response = login_user(client, username='nobody')
        assert b'Invalid username or password' in response.data

    def test_login_redirects_if_authenticated(self, client):
        register_user(client)
        login_user(client)
        # Already logged in — GET /auth/login should redirect
        response = client.get('/auth/login', follow_redirects=False)
        assert response.status_code == 302


class TestLogout:
    def test_logout(self, client):
        register_user(client)
        login_user(client)
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data

    def test_logout_requires_login(self, client):
        response = client.get('/auth/logout', follow_redirects=False)
        # Flask-Login redirects unauthenticated users to login page
        assert response.status_code == 302
