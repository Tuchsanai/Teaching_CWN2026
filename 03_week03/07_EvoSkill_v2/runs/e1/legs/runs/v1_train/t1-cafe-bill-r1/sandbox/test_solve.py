import unittest
from solve import cafe_bill

class T(unittest.TestCase):
    def test_values(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)
        self.assertEqual(cafe_bill([], True), 0)
        self.assertIs(type(cafe_bill([{"price": 1, "qty": 1}], True)), int)
    def test_reject(self):
        for items, m in [([{"price": 1, "qty": 0}], False), ([{"price": 1.0, "qty": 1}], False),
                         ([{"price": "1", "qty": 1}], False), ([{"price": True, "qty": 1}], False),
                         ([{"price": 1}], False), ([{"price": -1, "qty": 1}], False),
                         ([{"price": 1, "qty": 1}], 1), (None, False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

unittest.main() if __name__ == "__main__" else None
