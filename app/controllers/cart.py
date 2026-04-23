from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.cart import CartItem
from app.models.product import Product

cart = Blueprint('cart', __name__)


@cart.route('/')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(float(item.product.price) * item.quantity for item in cart_items)
    return render_template('cart/cart.html', cart_items=cart_items, total=total)


@cart.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json() or request.form
    try:
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

    if quantity > product.stock_quantity:
        return jsonify({'success': False, 'message': 'Insufficient stock'}), 400

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id, product_id=product_id, quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({
        'success': True,
        'message': 'Item added to cart',
        'cart_count': cart_count,
    })


@cart.route('/update', methods=['POST'])
@login_required
def update_cart():
    data = request.get_json() or request.form
    try:
        item_id = int(data.get('item_id'))
        quantity = int(data.get('quantity'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    cart_item = CartItem.query.filter_by(
        id=item_id, user_id=current_user.id
    ).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        product = db.session.get(Product, cart_item.product_id)
        if product and quantity > product.stock_quantity:
            return jsonify({'success': False, 'message': 'Insufficient stock'}), 400
        cart_item.quantity = quantity

    db.session.commit()
    return jsonify({'success': True, 'message': 'Cart updated'})


@cart.route('/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json() or request.form
    try:
        item_id = int(data.get('item_id'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    cart_item = CartItem.query.filter_by(
        id=item_id, user_id=current_user.id
    ).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item removed from cart'})
