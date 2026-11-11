"""L3.2 - characterization tests for add_to_cart. Same file runs on BEFORE and AFTER the AI refactor."""
from .base import CartBase


class AddToCartBehaviour(CartBase):
    def test_new_item_starts_at_1(self):
        self.add(self.burger); self.assertEqual(self.qty(self.burger), 1)

    def test_repeat_add_increments(self):
        self.add(self.burger, 3); self.assertEqual(self.qty(self.burger), 3)

    def test_legacy_dict_value_is_upgraded(self):
        s = self.client.session; s['cart'] = {str(self.burger.id): {'quantity': 4}}; s.save()
        self.add(self.burger); self.assertEqual(self.qty(self.burger), 5)

    def test_other_items_untouched(self):
        self.add(self.burger); self.add(self.fries)
        self.assertEqual((self.qty(self.burger), self.qty(self.fries)), (1, 1))

    def test_redirects_back_to_referer(self):
        r = self.client.get(f'/orders/cart/add/{self.burger.id}/', HTTP_REFERER='/restaurant/1/')
        self.assertEqual((r.status_code, r.url), (302, '/restaurant/1/'))

    def test_redirects_to_list_without_referer(self):
        r = self.client.get(f'/orders/cart/add/{self.burger.id}/')
        self.assertEqual(r.url, '/')

    def test_unknown_id_behaviour_is_preserved(self):
        self.client.get('/orders/cart/add/99999/')       # prototype stores it (DEF-05); refactor must not change this
        self.assertEqual(self.cart().get('99999'), 1)
