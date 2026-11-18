import unittest
from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill(one(10000), False), 10700)

    def test_member_only(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill(one(10000), True), 9630)

    def test_multiple_items(self):
        # 6000*2 + 5000*3 = 27000 -> *1.07 = 28890
        items = [{"price": 6000, "qty": 2}, {"price": 5000, "qty": 3}]
        self.assertEqual(cafe_bill(items, False), 28890)

    def test_threshold_exact(self):
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill(one(50000), False), 50825)

    def test_threshold_below(self):
        # 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill(one(49999), False), 53499)

    def test_threshold_above(self):
        # 50001*0.95*1.07 = 50825.50.. -> 50826
        self.assertEqual(cafe_bill(one(50001), False), 50826)

    def test_both_discounts(self):
        # 100000*0.95*0.9*1.07 = 91485
        self.assertEqual(cafe_bill(one(100000), True), 91485)

    def test_rounding_half_up(self):
        # 50 * 1.07 = 53.5 -> 54 (half up)
        self.assertEqual(cafe_bill(one(50), False), 54)

    def test_rounding_down(self):
        # 1 * 1.07 = 1.07 -> 1
        self.assertEqual(cafe_bill(one(1), False), 1)

    def test_result_is_int(self):
        self.assertIs(type(cafe_bill(one(12345, 3), True)), int)

    def test_reject_items(self):
        for bad in (None, (), {}, [], "x", [1], [{"price": 1}], [{"qty": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (1.5, 100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill(one(bad), False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill(one(100, bad), False)

    def test_reject_member(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cafe_bill(one(100), bad)

    def test_reject_bad_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}, {"price": 100, "qty": 0}], False)


if __name__ == "__main__":
    unittest.main()
