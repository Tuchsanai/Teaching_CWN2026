import unittest
from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_basic_vat(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_discount(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_and_threshold(self):
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], True), 45743)

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)

    def test_invalid(self):
        for items, m in [([{"price": 1.5, "qty": 1}], False),
                         ([{"price": 100, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 100, "qty": 1}], 1),
                         (None, False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
