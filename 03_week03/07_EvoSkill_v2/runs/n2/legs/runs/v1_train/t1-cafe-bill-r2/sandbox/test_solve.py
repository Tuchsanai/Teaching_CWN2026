import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half(self):
        # 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_reject(self):
        bad = [([{"price": 1, "qty": 0}], False), ([{"price": 1.0, "qty": 1}], False),
               ([{"price": "1", "qty": 1}], False), ([{"price": True, "qty": 1}], False),
               ([{"price": -1, "qty": 1}], False), ([{"price": 1}], False),
               ([1], False), (None, False), ([], 1), ([], None)]
        for a, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(a, m)


unittest.main() if __name__ == "__main__" else None
