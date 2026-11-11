"""Task D / L4.3 (version 1): plain Selenium script - add 3 items, apply coupon, place order.
Locators are repeated inline in the test (hard to maintain)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from orders.models import Order
from .selenium_base import SeleniumBase


class OrderFlowLinear(SeleniumBase):
    def test_S1_save10(self):
        d = self.driver
        self.login_by_cookie()
        d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')
        assert len(d.find_elements(By.CSS_SELECTOR, 'a.btn-card')) == 3       # "+ Add" buttons
        for i in range(3):
            d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')       # re-find after each reload
            d.find_elements(By.CSS_SELECTOR, 'a.btn-card')[i].click()
        d.get(f'{self.live_server_url}/orders/cart/')
        d.find_element(By.ID, 'coupon').send_keys('SAVE10')
        d.find_element(By.ID, 'apply-coupon').click()
        WebDriverWait(d, 5).until(EC.presence_of_element_located((By.ID, 'subtotal')))
        self.assertEqual(d.find_element(By.ID, 'total').text, '13.03')      # 14.48 - 1.45 (10 % of 14.48 = 1.448 -> 1.45)
        self.shot('selenium_cart_coupon')
        d.find_element(By.ID, 'checkout-link').click()
        d.find_element(By.NAME, 'full_name').send_keys('Alice Rao')
        d.find_element(By.NAME, 'phone_number').send_keys('+91 98765 43210')
        d.find_element(By.NAME, 'address').send_keys('12 MG Road, Pune')
        self.shot('selenium_checkout')
        d.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('/orders/history/', d.current_url)
        self.shot('selenium_history')
        o = Order.objects.get()
        self.assertEqual(o.items.count(), 3)

    def test_S2_flat5(self):
        d = self.driver
        self.login_by_cookie()
        d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')
        assert len(d.find_elements(By.CSS_SELECTOR, 'a.btn-card')) == 3       # "+ Add" buttons
        for i in range(3):
            d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')       # re-find after each reload
            d.find_elements(By.CSS_SELECTOR, 'a.btn-card')[i].click()
        d.get(f'{self.live_server_url}/orders/cart/')
        d.find_element(By.ID, 'coupon').send_keys('FLAT5')
        d.find_element(By.ID, 'apply-coupon').click()
        WebDriverWait(d, 5).until(EC.presence_of_element_located((By.ID, 'subtotal')))
        self.assertEqual(d.find_element(By.ID, 'total').text, '9.48')      # 14.48 - 1.45 (10 % of 14.48 = 1.448 -> 1.45)
        d.find_element(By.ID, 'checkout-link').click()
        d.find_element(By.NAME, 'full_name').send_keys('Alice Rao')
        d.find_element(By.NAME, 'phone_number').send_keys('+91 98765 43210')
        d.find_element(By.NAME, 'address').send_keys('12 MG Road, Pune')
        d.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('/orders/history/', d.current_url)
        o = Order.objects.get()
        self.assertEqual(o.items.count(), 3)

    def test_S3_invalid_coupon(self):
        d = self.driver
        self.login_by_cookie()
        d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')
        assert len(d.find_elements(By.CSS_SELECTOR, 'a.btn-card')) == 3       # "+ Add" buttons
        for i in range(3):
            d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')       # re-find after each reload
            d.find_elements(By.CSS_SELECTOR, 'a.btn-card')[i].click()
        d.get(f'{self.live_server_url}/orders/cart/')
        d.find_element(By.ID, 'coupon').send_keys('FREEFOOD')
        d.find_element(By.ID, 'apply-coupon').click()
        WebDriverWait(d, 5).until(EC.presence_of_element_located((By.ID, 'subtotal')))
        self.assertEqual(d.find_element(By.ID, 'total').text, '14.48')      # 14.48 - 1.45 (10 % of 14.48 = 1.448 -> 1.45)
        d.find_element(By.ID, 'checkout-link').click()
        d.find_element(By.NAME, 'full_name').send_keys('Alice Rao')
        d.find_element(By.NAME, 'phone_number').send_keys('+91 98765 43210')
        d.find_element(By.NAME, 'address').send_keys('12 MG Road, Pune')
        d.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('/orders/history/', d.current_url)
        o = Order.objects.get()
        self.assertEqual(o.items.count(), 3)
