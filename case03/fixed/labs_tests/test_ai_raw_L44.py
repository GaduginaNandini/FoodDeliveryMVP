"""L4.4 - the raw test set returned by AI (A1..A12), BEFORE human filtering.
Validity is judged against the requirements (FR-03..FR-08), not against what the code happens to do."""
from decimal import Decimal
from orders.models import Order
from .base import CartBase


class RawAISet(CartBase):
    def test_A01_add_returns_redirect(self):
        self.assertEqual(self.client.get(f'/orders/cart/add/{self.burger.id}/').status_code, 302)

    def test_A02_quantity_increments(self):
        self.add(self.burger, 2); self.assertEqual(self.qty(self.burger), 2)

    def test_A03_minus_never_goes_negative(self):
        self.client.get(f'/orders/cart/remove/{self.burger.id}/'); self.assertEqual(self.qty(self.burger), 0)

    def test_A04_cart_total_correct(self):
        self.add(self.burger); self.add(self.cola)
        self.assertEqual(self.client.get('/orders/cart/').context['total_price'], Decimal('10.49'))

    def test_A05_anonymous_checkout_blocked(self):
        self.add(self.burger); self.assertEqual(self.client.get('/orders/checkout/').status_code, 302)

    def test_A06_order_saves_items_and_clears_cart(self):
        self.login(); self.add(self.burger); self.client.post('/orders/checkout/', self.DETAILS)
        self.assertEqual(Order.objects.get().items.count(), 1); self.assertEqual(self.cart(), {})

    def test_A07_order_saves_delivery_address(self):
        self.login(); self.add(self.burger); self.client.post('/orders/checkout/', self.DETAILS)
        self.assertEqual(Order.objects.get().address, self.DETAILS['address'])

    def test_A08_order_history_lists_orders(self):
        self.login(); self.add(self.burger); self.client.post('/orders/checkout/', self.DETAILS)
        self.assertContains(self.client.get('/orders/history/'), 'Order #')

    # ---- hallucinated / not in the requirements -------------------------------------------------
    def test_A09_add_to_cart_must_be_POST_only(self):          # not a requirement of the prototype
        self.assertEqual(self.client.get(f'/orders/cart/add/{self.burger.id}/').status_code, 405)

    def test_A10_cart_adds_5_percent_tax(self):                 # no tax in the scenario
        self.add(self.burger)
        self.assertEqual(self.client.get('/orders/cart/').context['total_price'], Decimal('9.44'))

    def test_A11_out_of_stock_message_shown(self):              # no stock/inventory concept; only is_available
        r = self.client.get(f'/orders/cart/add/{self.sold_out.id}/', follow=True)
        self.assertContains(r, 'out of stock')

    def test_A12_cart_endpoint_returns_json(self):              # app renders HTML templates
        self.assertEqual(self.client.get('/orders/cart/')['Content-Type'], 'application/json')
