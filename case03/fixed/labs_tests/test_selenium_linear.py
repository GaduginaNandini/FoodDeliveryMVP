"""Task D / L4.3 (version 1): plain Selenium script - add 3 items, apply coupon, place order.
Locators are repeated inline in the test (hard to maintain).
Every step that loads a page waits for the page change before the next step."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from orders.models import Order
from .selenium_base import SeleniumBase


def wait(driver, seconds=10):
    return WebDriverWait(driver, seconds)


class OrderFlowLinear(SeleniumBase):
    def test_S1_save10(self):
        d = self.driver
        self.login_by_cookie()
        d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')
        assert len(d.find_elements(By.CSS_SELECTOR, 'a.btn-card')) == 3       # "+ Add" buttons
        for i in range(3):
            d.get(f'{self.live_server_url}/restaurant/{self.rest.id}/')       # re-find after each reload
            add = d.find_elements(By.CSS_SELECTOR, 'a.btn-card')[i]
            add.click()
            wait(d).until(EC.staleness_of(add))                               # the add request finished
        d.get(f'{self.live_server_url}/orders/cart/')
        d.find_element(By.ID, 'coupon').send_keys('SAVE10')
        apply_button = d.find_element(By.ID, 'apply-coupon')
        apply_button.click()
        wait(d).until(EC.staleness_of(apply_button))                          # cart page reloaded
        wait(d).until(EC.presence_of_element_located((By.ID, 'total')))
        self.assertEqual(d.find_element(By.ID, 'total').text, '13.03')      # 14.48 - 1.45 (10 % of 14.48 = 1.448 -> 1.45)
        self.shot('selenium_cart_coupon')
        d.find_element(By.ID, 'checkout-link').click()
        wait(d).until(EC.url_contains('/orders/checkout/'))
        d.find_element(By.NAME, 'full_name').send_keys('Alice Rao')
        d.find_element(By.NAME, 'phone_number').send_keys('+91 98765 43210')
        d.find_element(By.NAME, 'address').send_keys('12 MG Road, Pune')
        self.shot('selenium_checkout')
        submit = d.find_element(By.CSS_SELECTOR, 'button.btn-submit')
        submit.click()
        wait(d).until(EC.staleness_of(submit))                                # the server answered
        wait(d).until(EC.url_contains('/orders/history/'))
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
            add = d.find_elements(By.CSS_SELECTOR, 'a.btn-card')[i]
            add.click()
            wait(d).until(EC.staleness_of(add))                               # the add request finished
        d.get(f'{self.live_server_url}/orders/cart/')
        d.find_element(By.ID, 'coupon').send_keys('FLAT5')
        apply_button = d.find_element(By.ID, 'apply-coupon')
        apply_button.click()
        wait(d).until(EC.staleness_of(apply_button))                          # cart page reloaded
        wait(d).until(EC.presence_of_element_located((By.ID, 'total')))
        self.assertEqual(d.find_element(By.ID, 'total').text, '9.48')      # 14.48 - 5.00
        d.find_element(By.ID, 'checkout-link').click()
        wait(d).until(EC.url_contains('/orders/checkout/'))
        d.find_element(By.NAME, 'full_name').send_keys('Alice Rao')
        d.find_element(By.NAME, 'phone_number').send_keys('+91 98765 43210')
        d.find_element(By.NAME, 'address').send_keys('12 MG Road, Pune')
        submit = d.find_element(By.CSS_SELECTOR, 'button.btn-submit')
        submit.click()
        wait(d).until(EC.staleness_of(submit))                                # the server answered
        wait(d).until(EC.url_contains('/orders/history/'))
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
            add = d.find_elements(By.CSS_SELECTOR, 'a.btn-card')[i]
            add.click()
            wait(d).until(EC.staleness_of(add))                               # the add request finished
        d.get(f'{self.live_server_url}/orders/cart/')
        d.find_element(By.ID, 'coupon').send_keys('FREEFOOD')
        apply_button = d.find_element(By.ID, 'apply-coupon')
        apply_button.click()
        wait(d).until(EC.staleness_of(apply_button))                          # cart page reloaded
        wait(d).until(EC.presence_of_element_located((By.ID, 'total')))
        self.assertEqual(d.find_element(By.ID, 'total').text, '14.48')      # invalid code: no discount
        d.find_element(By.ID, 'checkout-link').click()
        wait(d).until(EC.url_contains('/orders/checkout/'))
        d.find_element(By.NAME, 'full_name').send_keys('Alice Rao')
        d.find_element(By.NAME, 'phone_number').send_keys('+91 98765 43210')
        d.find_element(By.NAME, 'address').send_keys('12 MG Road, Pune')
        submit = d.find_element(By.CSS_SELECTOR, 'button.btn-submit')
        submit.click()
        wait(d).until(EC.staleness_of(submit))                                # the server answered
        wait(d).until(EC.url_contains('/orders/history/'))
        self.assertIn('/orders/history/', d.current_url)
        o = Order.objects.get()
        self.assertEqual(o.items.count(), 3)