"""Page Object Model: one class per page; locators live here and nowhere else.

Every action that loads a new page waits for that page to really load
(the old element goes stale / the URL changes) before the test reads it.
This removes the race where a script reads or clicks while the browser is
still reloading.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WAIT = 10  # seconds


class BasePage:
    def __init__(self, driver, base_url):
        self.driver, self.base = driver, base_url

    def wait(self, condition):
        return WebDriverWait(self.driver, WAIT).until(condition)


class MenuPage(BasePage):
    ADD_BUTTONS = (By.CSS_SELECTOR, 'a.btn-card')

    def open(self, restaurant_id):
        self.driver.get(f'{self.base}/restaurant/{restaurant_id}/')
        return self

    def add_first_n_items(self, restaurant_id, n):
        for i in range(n):
            self.open(restaurant_id)
            button = self.driver.find_elements(*self.ADD_BUTTONS)[i]
            button.click()
            self.wait(EC.staleness_of(button))      # the add request finished
        return self


class CartPage(BasePage):
    COUPON = (By.ID, 'coupon')
    APPLY = (By.ID, 'apply-coupon')
    TOTAL = (By.ID, 'total')
    CHECKOUT = (By.ID, 'checkout-link')

    def open(self):
        self.driver.get(f'{self.base}/orders/cart/')
        return self

    def apply_coupon(self, code):
        box = self.driver.find_element(*self.COUPON)
        box.clear()
        box.send_keys(code)
        apply_button = self.driver.find_element(*self.APPLY)
        apply_button.click()
        self.wait(EC.staleness_of(apply_button))    # the cart page was reloaded
        self.wait(EC.presence_of_element_located(self.TOTAL))
        return self

    def total(self):
        return self.driver.find_element(*self.TOTAL).text

    def proceed_to_checkout(self):
        self.driver.find_element(*self.CHECKOUT).click()
        self.wait(EC.url_contains('/orders/checkout/'))
        return CheckoutPage(self.driver, self.base)


class CheckoutPage(BasePage):
    NAME = (By.NAME, 'full_name')
    PHONE = (By.NAME, 'phone_number')
    ADDRESS = (By.NAME, 'address')
    SUBMIT = (By.CSS_SELECTOR, 'button.btn-submit')

    def place_order(self, name, phone, address):
        self.wait(EC.presence_of_element_located(self.NAME))
        self.driver.find_element(*self.NAME).send_keys(name)
        self.driver.find_element(*self.PHONE).send_keys(phone)
        self.driver.find_element(*self.ADDRESS).send_keys(address)
        submit = self.driver.find_element(*self.SUBMIT)
        submit.click()
        self.wait(EC.staleness_of(submit))          # the server answered
        return self