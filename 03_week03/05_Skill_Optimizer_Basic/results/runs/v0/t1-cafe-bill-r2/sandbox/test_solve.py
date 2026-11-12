import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_rounding(self):
        self.assertEqual(cafe_bill([{"price": 1, "qty": 5}], False), 5)
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)

    def test_invalid(self):
        for items, m in [("x", False), [[{"price": 1.5, "qty": 1}], False],
                         ([{"price": 1, "qty": 0}], False),
                         ([{"price": -1, "qty": 1}], False),
                         ([{"price": 1}], False),
                         ([{"price": 1, "qty": 1}], "yes")]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
