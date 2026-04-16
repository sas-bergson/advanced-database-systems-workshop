from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))

    from app.controllers.auth import auth as auth_blueprint
    from app.controllers.main import main as main_blueprint
    from app.controllers.products import products as products_blueprint
    from app.controllers.orders import orders as orders_blueprint
    from app.controllers.cart import cart as cart_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(products_blueprint, url_prefix='/products')
    app.register_blueprint(orders_blueprint, url_prefix='/orders')
    app.register_blueprint(cart_blueprint, url_prefix='/cart')

    return app
