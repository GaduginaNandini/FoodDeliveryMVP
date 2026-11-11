"""Task D - equivalence classes + boundaries for quantity and coupon (EC-Q*, EC-C*).
Valid quantity per item = 1..20 (MAX_QTY).  Only meaningful on the lab-fixed copy."""
from decimal import Decimal
from .base import CartBase


class QuantityClasses(CartBase):
    def test_EC_Q1_valid_lower_boundary_1(self):
        self.add(self.burger, 1); self.assertEqual(self.qty(self.burger), 1)

    def test_EC_Q2_valid_typical_5(self):
        self.add(self.burger, 5); self.assertEqual(self.qty(self.burger), 5)

    def test_EC_Q3_valid_upper_boundary_20(self):
        self.add(self.burger, 20); self.assertEqual(self.qty(self.burger), 20)

    def test_EC_Q4_invalid_above_max_21_is_capped(self):
        self.add(self.burger, 21); self.assertEqual(self.qty(self.burger), 20)

    def test_EC_Q5_invalid_zero_or_below_removes_line(self):
        self.add(self.burger)
        self.client.get(f'/orders/cart/remove/{self.burger.id}/')       # 1 -> 0
        self.client.get(f'/orders/cart/remove/{self.burger.id}/')       # 0 -> stays absent, never negative
        self.assertEqual(self.qty(self.burger), 0)


class CouponClasses(CartBase):
    def _total(self, code=None, times=2):
        self.add(self.burger, times)            # subtotal 17.98
        if code is not None:
            self.client.post('/orders/cart/coupon/', {'coupon': code})
        return self.client.get('/orders/cart/').context['total_price']

    def test_EC_C1_valid_percent_coupon(self):
        self.assertEqual(self._total('SAVE10'), Decimal('16.18'))        # 17.98 - 1.80

    def test_EC_C2_valid_flat_coupon(self):
        self.assertEqual(self._total('FLAT5'), Decimal('12.98'))

    def test_EC_C3_valid_lowercase_and_spaces(self):
        self.assertEqual(self._total(' save10 '), Decimal('16.18'))

    def test_EC_C4_invalid_unknown_code_no_discount(self):
        self.assertEqual(self._total('FREEFOOD'), Decimal('17.98'))

    def test_EC_C5_invalid_empty_code_no_discount(self):
        self.assertEqual(self._total(''), Decimal('17.98'))

    def test_EC_C6_boundary_flat_larger_than_subtotal_total_not_negative(self):
        self.add(self.cola)                       # 1.50
        self.client.post('/orders/cart/coupon/', {'coupon': 'FLAT5'})
        self.assertEqual(self.client.get('/orders/cart/').context['total_price'], Decimal('0.00'))

    def test_EC_C7_discount_is_stored_in_order_total(self):
        from orders.models import Order
        self.login(); self.add(self.burger, 2)
        self.client.post('/orders/cart/coupon/', {'coupon': 'SAVE10'})
        self.client.post('/orders/checkout/', self.DETAILS)
        self.assertEqual(Order.objects.get().total_amount, Decimal('16.18'))
