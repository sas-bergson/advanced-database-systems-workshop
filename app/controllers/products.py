from flask import Blueprint, render_template, request
from app.models.product import Product

products = Blueprint('products', __name__)


@products.route('/')
def list_products():
    search = request.args.get('search', '').strip()
    query = Product.query.filter_by(is_active=True)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    products_list = query.order_by(Product.name).all()
    return render_template('products/list.html', products=products_list, search=search)


@products.route('/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('products/detail.html', product=product)
