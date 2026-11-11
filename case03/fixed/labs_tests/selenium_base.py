"""Shared Selenium plumbing: live server (Django test DB), headless Chrome, session-cookie login.
The cookie login is needed because /accounts/login/ is broken in the original prototype (DEF-02)."""
import os, shutil
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from restaurants.models import Restaurant, FoodItem

SHOTS = os.environ.get('SHOT_DIR', '/tmp/shots')


class SeleniumBase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        o = Options()
        o.binary_location = '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'
        for a in ('--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1280,900'):
            o.add_argument(a)
        cls.driver = webdriver.Chrome(service=Service(os.environ.get('CHROMEDRIVER') or shutil.which('chromedriver')), options=o)
        cls.driver.implicitly_wait(3)
        os.makedirs(SHOTS, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.rest = Restaurant.objects.create(name='Burger Joint', description='Gourmet burgers', cuisine='Fast Food',
                                              address='1 Main St', delivery_time='25-35 mins', image_url='')
        mk = lambda n, p: FoodItem.objects.create(restaurant=self.rest, name=n, price=Decimal(p), category='c', image_url='')
        self.burger, self.fries, self.cola = mk('Cheeseburger', '8.99'), mk('Crispy Fries', '3.99'), mk('Cola', '1.50')
        self.user = User.objects.create_user('alice', password='pw12345!x')

    def login_by_cookie(self):
        from django.test import Client
        c = Client(); c.force_login(self.user)
        self.driver.get(self.live_server_url + '/restaurant/%d/' % self.rest.id)
        self.driver.add_cookie({'name': 'sessionid', 'value': c.cookies['sessionid'].value, 'path': '/'})

    def shot(self, name):
        self.driver.save_screenshot(os.path.join(SHOTS, name + '.png'))
