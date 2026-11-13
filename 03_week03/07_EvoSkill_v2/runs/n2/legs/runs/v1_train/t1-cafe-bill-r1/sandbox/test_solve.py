import unittest
from solve import cafe_bill

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([], False), 0)
    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)  # 45742.5 -> up
    def test_reject(self):
        for items, m in [([{"price": 0.5, "qty": 1}], False), ([{"price": 100, "qty": 0}], False),
                         ([{"price": 100, "qty": True}], False), ([{"price": -1, "qty": 1}], False),
                         ([{"price": "1", "qty": 1}], False), ([{"price": 1}], False),
                         ([1], False), (None, False), ([], 1), ([], None)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)
unittest.main() if __name__ == "__main__" else None
