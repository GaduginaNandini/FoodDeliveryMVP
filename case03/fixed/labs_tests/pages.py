"""Page Object Model: one class per page; locators live here and nowhere else."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, base_url):
        self.driver, self.base = driver, base_url


class MenuPage(BasePage):
    ADD_BUTTONS = (By.CSS_SELECTOR, 'a.btn-card')

    def open(self, restaurant_id):
        self.driver.get(f'{self.base}/restaurant/{restaurant_id}/')
        return self

    def add_first_n_items(self, restaurant_id, n):
        for i in range(n):
            self.open(restaurant_id)
            self.driver.find_elements(*self.ADD_BUTTONS)[i].click()
        return self


class CartPage(BasePage):
    COUPON = (By.ID, 'coupon'); APPLY = (By.ID, 'apply-coupon')
    TOTAL = (By.ID, 'total'); CHECKOUT = (By.ID, 'checkout-link')

    def open(self):
        self.driver.get(f'{self.base}/orders/cart/'); return self

    def apply_coupon(self, code):
        self.driver.find_element(*self.COUPON).send_keys(code)
        self.driver.find_element(*self.APPLY).click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'subtotal')))  # page reloaded
        return self

    def total(self):
        return self.driver.find_element(*self.TOTAL).text

    def proceed_to_checkout(self):
        self.driver.find_element(*self.CHECKOUT).click(); return CheckoutPage(self.driver, self.base)


class CheckoutPage(BasePage):
    NAME = (By.NAME, 'full_name'); PHONE = (By.NAME, 'phone_number')
    ADDRESS = (By.NAME, 'address'); SUBMIT = (By.CSS_SELECTOR, 'button.btn-submit')

    def place_order(self, name, phone, address):
        self.driver.find_element(*self.NAME).send_keys(name)
        self.driver.find_element(*self.PHONE).send_keys(phone)
        self.driver.find_element(*self.ADDRESS).send_keys(address)
        self.driver.find_element(*self.SUBMIT).click()
