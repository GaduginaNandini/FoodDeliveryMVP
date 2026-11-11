"""L4.3 (version 2): the same scenario with the Page Object Model."""
from orders.models import Order
from .pages import MenuPage, CartPage
from .selenium_base import SeleniumBase


class OrderFlowPOM(SeleniumBase):
    def test_S1_save10(self):
        self.login_by_cookie()
        MenuPage(self.driver, self.live_server_url).add_first_n_items(self.rest.id, 3)
        cart = CartPage(self.driver, self.live_server_url).open().apply_coupon('SAVE10')
        self.assertEqual(cart.total(), '13.03')
        cart.proceed_to_checkout().place_order('Alice Rao', '+91 98765 43210', '12 MG Road, Pune')
        self.assertIn('/orders/history/', self.driver.current_url)
        self.assertEqual(Order.objects.get().items.count(), 3)

    def test_S2_flat5(self):
        self.login_by_cookie()
        MenuPage(self.driver, self.live_server_url).add_first_n_items(self.rest.id, 3)
        cart = CartPage(self.driver, self.live_server_url).open().apply_coupon('FLAT5')
        self.assertEqual(cart.total(), '9.48')
        cart.proceed_to_checkout().place_order('Alice Rao', '+91 98765 43210', '12 MG Road, Pune')
        self.assertIn('/orders/history/', self.driver.current_url)
        self.assertEqual(Order.objects.get().items.count(), 3)

    def test_S3_invalid_coupon(self):
        self.login_by_cookie()
        MenuPage(self.driver, self.live_server_url).add_first_n_items(self.rest.id, 3)
        cart = CartPage(self.driver, self.live_server_url).open().apply_coupon('FREEFOOD')
        self.assertEqual(cart.total(), '14.48')
        cart.proceed_to_checkout().place_order('Alice Rao', '+91 98765 43210', '12 MG Road, Pune')
        self.assertIn('/orders/history/', self.driver.current_url)
        self.assertEqual(Order.objects.get().items.count(), 3)
