import pytest
from app.models import db
from app.models.user import User
from app.models.product import Category, Product
from app.models.order import Order, OrderItem
from app.models.cart import CartItem


class TestUserModel:
    def test_user_creation(self, app):
        with app.app_context():
            user = User(username='alice', email='alice@example.com')
            user.set_password('secret123')
            db.session.add(user)
            db.session.commit()

            fetched = db.session.get(User, user.id)
            assert fetched is not None
            assert fetched.username == 'alice'
            assert fetched.email == 'alice@example.com'
            assert fetched.is_admin is False

    def test_password_hashing(self, app):
        with app.app_context():
            user = User(username='bob', email='bob@example.com')
            user.set_password('mypassword')
            db.session.add(user)
            db.session.commit()

            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False

    def test_password_not_stored_in_plaintext(self, app):
        with app.app_context():
            user = User(username='carol', email='carol@example.com')
            user.set_password('supersecret')
            assert user.password_hash != 'supersecret'

    def test_to_dict_excludes_password(self, app):
        with app.app_context():
            user = User(username='dave', email='dave@example.com')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

            d = user.to_dict()
            assert 'password_hash' not in d
            assert d['username'] == 'dave'
            assert d['email'] == 'dave@example.com'

    def test_username_uniqueness(self, app):
        with app.app_context():
            u1 = User(username='unique', email='u1@example.com')
            u1.set_password('pass')
            db.session.add(u1)
            db.session.commit()

            u2 = User(username='unique', email='u2@example.com')
            u2.set_password('pass')
            db.session.add(u2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()


class TestCategoryModel:
    def test_category_creation(self, app):
        with app.app_context():
            cat = Category(name='Electronics', description='Gadgets and devices')
            db.session.add(cat)
            db.session.commit()

            fetched = db.session.get(Category, cat.id)
            assert fetched.name == 'Electronics'

    def test_category_to_dict(self, app):
        with app.app_context():
            cat = Category(name='Books', description='All kinds of books')
            db.session.add(cat)
            db.session.commit()
            d = cat.to_dict()
            assert d['name'] == 'Books'
            assert 'id' in d


class TestProductModel:
    def test_product_creation(self, app):
        with app.app_context():
            cat = Category(name='Clothing', description='Apparel')
            db.session.add(cat)
            db.session.commit()

            product = Product(
                name='T-Shirt',
                description='Cotton t-shirt',
                price=19.99,
                stock_quantity=50,
                category_id=cat.id,
            )
            db.session.add(product)
            db.session.commit()

            assert product.id is not None
            assert float(product.price) == 19.99
            assert product.is_active is True

    def test_is_in_stock(self, app):
        with app.app_context():
            p_in = Product(name='Available', price=10.00, stock_quantity=5)
            p_out = Product(name='Sold Out', price=10.00, stock_quantity=0)
            db.session.add_all([p_in, p_out])
            db.session.commit()

            assert p_in.is_in_stock() is True
            assert p_out.is_in_stock() is False

    def test_product_to_dict(self, app):
        with app.app_context():
            p = Product(name='Widget', price=5.50, stock_quantity=10)
            db.session.add(p)
            db.session.commit()
            d = p.to_dict()
            assert d['name'] == 'Widget'
            assert d['price'] == 5.50


class TestOrderModel:
    def test_order_creation(self, app):
        with app.app_context():
            user = User(username='orderuser', email='order@example.com')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

            order = Order(user_id=user.id, status='pending', total_amount=99.99)
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.status == 'pending'

    def test_order_to_dict(self, app):
        with app.app_context():
            user = User(username='dictuser', email='dict@example.com')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

            order = Order(user_id=user.id, total_amount=50.00)
            db.session.add(order)
            db.session.commit()

            d = order.to_dict()
            assert d['status'] == 'pending'
            assert d['total_amount'] == 50.00

    def test_calculate_total(self, app):
        with app.app_context():
            user = User(username='totaluser', email='total@example.com')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

            order = Order(user_id=user.id, total_amount=0)
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                product_id=None,
                quantity=3,
                unit_price=10.00,
            )
            # Manually set for calculation without FK
            order.items.append(item)
            total = order.calculate_total()
            assert float(total) == 30.00


class TestCartItemModel:
    def test_cart_item_creation(self, app):
        with app.app_context():
            user = User(username='cartuser', email='cart@example.com')
            user.set_password('pass')
            product = Product(name='Cart Product', price=15.00, stock_quantity=20)
            db.session.add_all([user, product])
            db.session.commit()

            ci = CartItem(user_id=user.id, product_id=product.id, quantity=2)
            db.session.add(ci)
            db.session.commit()

            assert ci.id is not None
            assert ci.quantity == 2

    def test_cart_item_to_dict(self, app):
        with app.app_context():
            user = User(username='cartdict', email='cartdict@example.com')
            user.set_password('pass')
            product = Product(name='Dict Product', price=5.00, stock_quantity=5)
            db.session.add_all([user, product])
            db.session.commit()

            ci = CartItem(user_id=user.id, product_id=product.id, quantity=1)
            db.session.add(ci)
            db.session.commit()

            d = ci.to_dict()
            assert d['quantity'] == 1
            assert 'user_id' in d
