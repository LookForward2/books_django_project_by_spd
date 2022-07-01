from django.test import TestCase
from store.logic import operations

class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(6, 8, '+')
        self.assertEqual(14, result)
    def test_minus(self):
        result = operations(6, 8, '-')
        self.assertEqual(-2, result)