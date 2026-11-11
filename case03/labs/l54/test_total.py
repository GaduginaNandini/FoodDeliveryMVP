import importlib, sys, unittest
from decimal import Decimal
P = {'1': Decimal('8.99'), '2': Decimal('3.99'), '3': Decimal('1.50')}

class Base:
    mod = None
    def f(self, cart): return importlib.import_module(self.mod).cart_total(cart, P)
    def test_01_empty_cart_is_zero(self):            self.assertEqual(self.f({}), 0)
    def test_02_single_item(self):                   self.assertEqual(self.f({'1': 1}), Decimal('8.99'))
    def test_03_quantity_multiplies(self):           self.assertEqual(self.f({'1': 3}), Decimal('26.97'))
    def test_04_multiple_items(self):                self.assertEqual(self.f({'1': 2, '2': 1, '3': 4}), Decimal('27.97'))
    def test_05_legacy_dict_value(self):             self.assertEqual(self.f({'2': {'quantity': 2}}), Decimal('7.98'))
    def test_06_unknown_item_ignored(self):          self.assertEqual(self.f({'99': 5, '1': 1}), Decimal('8.99'))
    def test_07_integer_item_ids(self):              self.assertEqual(self.f({1: 2}), Decimal('17.98'))
    def test_08_corrupt_quantity_does_not_crash(self): self.assertEqual(self.f({'1': 'abc'}), 0)
    def test_09_negative_quantity_not_priced(self):  self.assertEqual(self.f({'1': -2}), 0)
    def test_10_quantity_capped_at_20(self):         self.assertEqual(self.f({'3': 50}), Decimal('30.00'))

class Manual(Base, unittest.TestCase): mod = 'total_manual'
class AI(Base, unittest.TestCase):     mod = 'total_ai'
if __name__ == '__main__': unittest.main(verbosity=2)
