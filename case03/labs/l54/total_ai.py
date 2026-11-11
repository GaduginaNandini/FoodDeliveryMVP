"""AI version: same job, generated with the prompt in Appendix A (step 'L5.4')."""
from decimal import Decimal

MAX_QTY = 20


def _quantity(value):
    """Return a safe quantity 0..MAX_QTY from an int, numeric string, or legacy {'quantity': n} dict."""
    raw = value.get('quantity', 0) if isinstance(value, dict) else value
    try:
        return max(0, min(int(raw), MAX_QTY))
    except (TypeError, ValueError):
        return 0


def cart_total(cart, prices):
    """Sum price x quantity for every cart line whose item has a known price."""
    return sum(
        (prices[str(item_id)] * _quantity(value) for item_id, value in cart.items() if str(item_id) in prices),
        Decimal('0.00'),
    )
