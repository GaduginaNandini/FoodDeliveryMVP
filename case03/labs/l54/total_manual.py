"""Manual version: the cart-total loop as written in the prototype's view_cart(), lifted into a pure function."""
from decimal import Decimal


def cart_total(cart, prices):
    total = 0
    for item_id, val in cart.items():
        try:
            price = prices[str(item_id)]
            quantity = val.get('quantity', 1) if isinstance(val, dict) else int(val)
            subtotal = price * quantity
            total += subtotal
        except KeyError:
            continue
    return total
