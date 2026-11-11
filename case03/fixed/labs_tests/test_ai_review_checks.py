"""L5.3 - every AI review suggestion is tested before it is accepted (R1..R8).
Each test asserts the DESIRED behaviour; a failure on the pre-review code proves the AI was right."""
from unittest import mock
from django.contrib.auth.models import User
from orders.models import Order, OrderItem
from .base import CartBase


class ReviewSuggestions(CartBase):
    def test_R1_order_and_items_are_atomic(self):
        self.login(); self.add(self.burger); self.add(self.fries)
        real = OrderItem.objects.create
        calls = {'n': 0}
        def flaky(*a, **k):
            calls['n'] += 1
            if calls['n'] == 2: raise RuntimeError('db hiccup')
            return real(*a, **k)
        with mock.patch.object(OrderItem.objects, 'create', side_effect=flaky):
            with self.assertRaises(RuntimeError):
                self.client.post('/orders/checkout/', self.DETAILS)
        self.assertEqual(Order.objects.count(), 0, 'orphan Order left behind')

    def test_R2a_corrupt_quantity_does_not_crash_cart(self):
        s = self.client.session; s['cart'] = {str(self.burger.id): 'abc'}; s.save()
        self.assertEqual(self.client.get('/orders/cart/').status_code, 200)

    def test_R2b_zero_or_negative_quantity_never_priced(self):
        s = self.client.session; s['cart'] = {str(self.burger.id): -3}; s.save()
        self.assertEqual(self.client.get('/orders/cart/').context['total_price'], 0)

    def test_R3a_cart_views_should_not_change_state_on_GET(self):
        r = self.client.get(f'/orders/cart/add/{self.burger.id}/')
        self.assertEqual(r.status_code, 405)          # deliberately DEFERRED (templates use links)

    def test_R3b_no_open_redirect_via_referer(self):
        r = self.client.get(f'/orders/cart/add/{self.burger.id}/', HTTP_REFERER='https://evil.example/phish')
        self.assertNotIn('evil.example', r.url)

    def test_R4_free_order_not_possible(self):
        self.login(); self.add(self.cola)
        self.client.post('/orders/cart/coupon/', {'coupon': 'FLAT5'})
        r = self.client.post('/orders/checkout/', self.DETAILS)
        self.assertEqual(Order.objects.count(), 0)    # business decision: DEFERRED

    def test_R7_register_login_works_with_single_backend(self):
        r = self.client.post('/orders/register/', {'username': 'newuser', 'password1': 'Str0ng!pass9', 'password2': 'Str0ng!pass9'})
        self.assertEqual(r.status_code, 302)           # claim: ValueError with several backends - not our config

    def test_R8_order_history_query_count_constant(self):
        self.login()
        for i in range(3):
            o = Order.objects.create(user=self.user, full_name='A', phone_number='1', address='x')
            OrderItem.objects.create(order=o, food_item=self.burger, quantity=1, price=self.burger.price)
        with self.assertNumQueries(3):                 # session, user, orders  (no per-order item queries)
            self.client.get('/orders/history/')
