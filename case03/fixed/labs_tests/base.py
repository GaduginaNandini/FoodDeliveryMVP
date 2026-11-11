from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from restaurants.models import Restaurant, FoodItem


class CartBase(TestCase):
    """Shared fixture: 1 restaurant, 3 available items + 1 unavailable item."""

    def setUp(self):
        self.rest = Restaurant.objects.create(name='Burger Joint', description='d', cuisine='Fast Food',
                                              address='1 Main St', delivery_time='25 mins')
        mk = lambda n, p, avail=True: FoodItem.objects.create(
            restaurant=self.rest, name=n, price=Decimal(p), category='c', is_available=avail)
        self.burger = mk('Cheeseburger', '8.99')
        self.fries = mk('Crispy Fries', '3.99')
        self.cola = mk('Cola', '1.50')
        self.sold_out = mk('Sold Out Shake', '4.00', avail=False)
        self.user = User.objects.create_user('alice', password='pw12345!x')

    # helpers
    def add(self, item, times=1):
        for _ in range(times):
            self.client.get(f'/orders/cart/add/{item.id}/')

    def cart(self):
        return self.client.session.get('cart', {})

    def qty(self, item):
        v = self.cart().get(str(item.id), 0)
        return v.get('quantity', 0) if isinstance(v, dict) else v

    def login(self):
        self.client.force_login(self.user)

    DETAILS = {'full_name': 'Alice Rao', 'phone_number': '+91 98765 43210', 'address': '12 MG Road, Pune'}
