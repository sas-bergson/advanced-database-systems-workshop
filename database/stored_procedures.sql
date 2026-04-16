-- Stored procedure to create an order from cart items
CREATE OR REPLACE FUNCTION create_order_from_cart(p_user_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_order_id INTEGER;
    v_total NUMERIC(10, 2) := 0;
    v_cart_item RECORD;
BEGIN
    -- Check if cart is empty
    IF NOT EXISTS (SELECT 1 FROM cart_items WHERE user_id = p_user_id) THEN
        RAISE EXCEPTION 'Cart is empty for user %', p_user_id;
    END IF;

    -- Validate stock for all cart items
    FOR v_cart_item IN
        SELECT ci.product_id, ci.quantity, p.stock_quantity, p.price
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = p_user_id
    LOOP
        IF v_cart_item.quantity > v_cart_item.stock_quantity THEN
            RAISE EXCEPTION 'Insufficient stock for product %', v_cart_item.product_id;
        END IF;
    END LOOP;

    -- Create the order
    INSERT INTO orders (user_id, status, total_amount)
    VALUES (p_user_id, 'pending', 0)
    RETURNING id INTO v_order_id;

    -- Move cart items to order items and update inventory
    FOR v_cart_item IN
        SELECT ci.product_id, ci.quantity, p.price
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = p_user_id
    LOOP
        -- Insert order item
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (v_order_id, v_cart_item.product_id, v_cart_item.quantity, v_cart_item.price);

        -- Update product stock
        UPDATE products
        SET stock_quantity = stock_quantity - v_cart_item.quantity
        WHERE id = v_cart_item.product_id;

        -- Add to total
        v_total := v_total + (v_cart_item.price * v_cart_item.quantity);
    END LOOP;

    -- Update order total
    UPDATE orders SET total_amount = v_total WHERE id = v_order_id;

    -- Clear the cart
    DELETE FROM cart_items WHERE user_id = p_user_id;

    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql;

-- Stored procedure to update order status with validated transitions
CREATE OR REPLACE FUNCTION update_order_status(p_order_id INTEGER, p_new_status VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_status VARCHAR;
    v_valid_transitions BOOLEAN := FALSE;
BEGIN
    -- Get current status
    SELECT status INTO v_current_status FROM orders WHERE id = p_order_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order % not found', p_order_id;
    END IF;

    -- Validate status transition
    CASE v_current_status
        WHEN 'pending' THEN
            v_valid_transitions := p_new_status IN ('processing', 'cancelled');
        WHEN 'processing' THEN
            v_valid_transitions := p_new_status IN ('shipped', 'cancelled');
        WHEN 'shipped' THEN
            v_valid_transitions := p_new_status = 'delivered';
        ELSE
            v_valid_transitions := FALSE;
    END CASE;

    IF NOT v_valid_transitions THEN
        RAISE EXCEPTION 'Invalid status transition from % to %', v_current_status, p_new_status;
    END IF;

    -- Update the status
    UPDATE orders
    SET status = p_new_status, updated_at = CURRENT_TIMESTAMP
    WHERE id = p_order_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get cart total for a user
CREATE OR REPLACE FUNCTION get_cart_total(p_user_id INTEGER)
RETURNS NUMERIC(10, 2) AS $$
DECLARE
    v_total NUMERIC(10, 2);
BEGIN
    SELECT COALESCE(SUM(ci.quantity * p.price), 0)
    INTO v_total
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.id
    WHERE ci.user_id = p_user_id;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;
