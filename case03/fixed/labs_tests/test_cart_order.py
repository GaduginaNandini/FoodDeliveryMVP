"""Unit + integration tests (IDs UT-xx, IT-xx).  Fixed copy only for helper-level tests."""
from decimal import Decimal
from orders.models import Order, OrderItem
from .base import CartBase


class UnitTests(CartBase):
    def test_UT_01_qty_reads_int_and_legacy_dict(self):
        from orders.views import _qty
        self.assertEqual(_qty(3), 3)
        self.assertEqual(_qty({'quantity': 4}), 4)

    def test_UT_02_order_str(self):
        o = Order.objects.create(user=self.user, full_name='A', phone_number='1', address='x')
        self.assertEqual(str(o), f'Order #{o.id} - A')

    def test_UT_03_orderitem_str(self):
        o = Order.objects.create(user=self.user, full_name='A', phone_number='1', address='x')
        oi = OrderItem.objects.create(order=o, food_item=self.burger, quantity=2, price=self.burger.price)
        self.assertEqual(str(oi), '2 x Cheeseburger')

    def test_UT_04_discount_percent_flat_and_cap(self):
        from orders.views import discount_for
        self.assertEqual(discount_for('SAVE10', Decimal('20.00')), Decimal('2.00'))
        self.assertEqual(discount_for('FLAT5', Decimal('20.00')), Decimal('5.00'))
        self.assertEqual(discount_for('FLAT5', Decimal('3.00')), Decimal('3.00'))
        self.assertEqual(discount_for('NOPE', Decimal('20.00')), Decimal('0.00'))


class IntegrationTests(CartBase):
    def test_IT_01_browse_menu_add_view_cart(self):
        self.assertEqual(self.client.get(f'/restaurant/{self.rest.id}/').status_code, 200)
        self.add(self.burger)
        r = self.client.get('/orders/cart/')
        self.assertContains(r, 'Cheeseburger')

    def test_IT_02_full_order_flow_and_history(self):
        self.login(); self.add(self.burger); self.add(self.cola, 2)
        self.client.post('/orders/checkout/', self.DETAILS)
        r = self.client.get('/orders/history/')
        self.assertContains(r, 'Alice Rao')
        self.assertContains(r, '11.99')       # 8.99 + 2*1.50

    def test_IT_03_history_shows_only_own_orders(self):
        from django.contrib.auth.models import User
        bob = User.objects.create_user('bob', password='pw12345!x')
        Order.objects.create(user=bob, full_name='Bob Only', phone_number='1', address='x')
        self.login()
        self.assertNotContains(self.client.get('/orders/history/'), 'Bob Only')

    def test_IT_04_checkout_page_shows_total(self):
        self.login(); self.add(self.burger)
        self.assertContains(self.client.get('/orders/checkout/'), '8.99')

    def test_IT_05_cannot_add_unavailable_item(self):
        r = self.client.get(f'/orders/cart/add/{self.sold_out.id}/')
        self.assertNotIn(str(self.sold_out.id), self.cart())

    def test_IT_06_cannot_add_nonexistent_item(self):
        self.client.get('/orders/cart/add/99999/')
        self.assertNotIn('99999', self.cart())

    def test_IT_07_home_page_loads_for_anonymous_visitor(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_IT_08_login_page_loads(self):
        self.assertEqual(self.client.get('/accounts/login/').status_code, 200)

    def test_IT_09_empty_delivery_details_rejected(self):
        self.login(); self.add(self.burger)
        self.client.post('/orders/checkout/', {'full_name': '', 'phone_number': '', 'address': ''})
        self.assertEqual(Order.objects.count(), 0)
