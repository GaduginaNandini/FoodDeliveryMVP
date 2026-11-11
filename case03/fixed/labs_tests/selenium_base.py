"""Shared Selenium plumbing for Django live-server tests."""

import os
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from restaurants.models import Restaurant, FoodItem


SHOTS = os.environ.get(
    'SHOT_DIR',
    os.path.join(os.getcwd(), 'selenium_shots')
)


class SeleniumBase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = Options()

        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280,900')

        # Selenium Manager automatically locates Chrome and its driver.
        cls.driver = webdriver.Chrome(options=options)

        cls.driver.implicitly_wait(3)

        os.makedirs(SHOTS, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()

        super().tearDownClass()

    def setUp(self):
        self.rest = Restaurant.objects.create(
            name='Burger Joint',
            description='Gourmet burgers',
            cuisine='Fast Food',
            address='1 Main St',
            delivery_time='25-35 mins',
            image_url=''
        )

        def create_item(name, price):
            return FoodItem.objects.create(
                restaurant=self.rest,
                name=name,
                price=Decimal(price),
                category='c',
                image_url=''
            )

        self.burger = create_item('Cheeseburger', '8.99')
        self.fries = create_item('Crispy Fries', '3.99')
        self.cola = create_item('Cola', '1.50')

        self.user = User.objects.create_user(
            'alice',
            password='pw12345!x'
        )

    def login_by_cookie(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        self.driver.get(
            self.live_server_url + '/restaurant/%d/' % self.rest.id
        )

        self.driver.add_cookie({
            'name': 'sessionid',
            'value': client.cookies['sessionid'].value,
            'path': '/'
        })

    def shot(self, name):
        self.driver.save_screenshot(
            os.path.join(SHOTS, name + '.png')
        )