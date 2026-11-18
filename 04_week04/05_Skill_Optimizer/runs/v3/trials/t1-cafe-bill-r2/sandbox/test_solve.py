import unittest
from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both_discounts(self):
        self.assertEqual(cafe_bill([{"price": 60000, "qty": 1}], True), 54891)

    def test_single_rounding(self):
        # 3 x 1 satang: 3*1.07 = 3.21 -> 3
        self.assertEqual(cafe_bill([{"price": 1, "qty": 3}], False), 3)
        # half rounds up: 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [([{"price": 1.5, "qty": 1}], False),
                         ([{"price": 100, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 100, "qty": 1}], 1),
                         ("x", False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
