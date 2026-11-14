import unittest
from solve import cafe_bill

class T(unittest.TestCase):
    def test_basic(self):
        r = cafe_bill([{"price": 10000, "qty": 5}], False)
        self.assertEqual(r, 50750 * 95 // 100 if False else round(50000*0.95*1.07))
        self.assertIs(type(r), int)
    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([], False), 0)
    def test_reject(self):
        for items, m in [([{"price": 1.0, "qty": 1}], False), ([{"price": 1, "qty": 0}], False),
                         ([{"price": 1}], False), ([{"price": True, "qty": 1}], False),
                         ([], 1), ("x", False), ([{"price": -1, "qty": 1}], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)
unittest.main() if __name__ == "__main__" else None
