from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.product import Product

orders = Blueprint('orders', __name__)


@orders.route('/')
@login_required
def list_orders():
    user_orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template('orders/list.html', orders=user_orders)


@orders.route('/<int:id>')
@login_required
def order_detail(id):
    order = Order.query.get_or_404(id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('orders.list_orders'))
    return render_template('orders/detail.html', order=order)


@orders.route('/create', methods=['POST'])
@login_required
def create_order():
    order_id = None
    try:
        # Attempt the PostgreSQL stored procedure first
        result = db.session.execute(
            db.text('SELECT create_order_from_cart(:user_id)'),
            {'user_id': current_user.id},
        )
        order_id = result.scalar()
        db.session.commit()
    except Exception:
        db.session.rollback()
        # Python/SQLAlchemy fallback (used for SQLite in tests)
        try:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            if not cart_items:
                flash('Your cart is empty.', 'warning')
                return redirect(url_for('cart.view_cart'))

            order = Order(user_id=current_user.id, status='pending', total_amount=0)
            db.session.add(order)
            db.session.flush()

            total = 0
            for item in cart_items:
                product = db.session.get(Product, item.product_id)
                if not product:
                    db.session.rollback()
                    flash(f'Product ID {item.product_id} no longer exists.', 'danger')
                    return redirect(url_for('cart.view_cart'))
                if product.stock_quantity < item.quantity:
                    db.session.rollback()
                    flash(f'Insufficient stock for {product.name}.', 'danger')
                    return redirect(url_for('cart.view_cart'))

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=product.price,
                )
                db.session.add(order_item)
                product.stock_quantity -= item.quantity
                total += float(product.price) * item.quantity

            order.total_amount = total
            CartItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            order_id = order.id
        except Exception as exc:
            db.session.rollback()
            flash(f'Error creating order: {exc}', 'danger')
            return redirect(url_for('cart.view_cart'))

    flash('Order placed successfully!', 'success')
    return redirect(url_for('orders.order_detail', id=order_id))


@orders.route('/<int:id>/status')
@login_required
def order_status(id):
    order = Order.query.get_or_404(id)
    if order.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify({
        'order_id': order.id,
        'status': order.status,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None,
    })
