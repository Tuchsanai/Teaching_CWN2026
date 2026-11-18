import unittest
from solve import cafe_bill


def I(price, qty=1):
    return {"price": price, "qty": qty}


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        # 10000 * 1.07 = 10700
        self.assertEqual(cafe_bill([I(10000)], False), 10700)

    def test_member_only(self):
        # 10000 * 0.9 * 1.07 = 9630
        self.assertEqual(cafe_bill([I(10000)], True), 9630)

    def test_multiple_items(self):
        # 5000*2 + 3000*3 = 19000 -> *1.07 = 20330
        self.assertEqual(cafe_bill([I(5000, 2), I(3000, 3)], False), 20330)

    def test_threshold_exact(self):
        # 50000 พอดี ลด 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([I(50000)], False), 50825)

    def test_below_threshold(self):
        # 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([I(49999)], False), 53499)

    def test_above_threshold(self):
        # 50001*.95*1.07 = 50825.5... -> 50826 (50001*10165/10000 = 50826.01665)
        self.assertEqual(cafe_bill([I(50001)], False), 50826)

    def test_both_discounts(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill([I(100000)], True), 91485)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54 (ครึ่งขึ้น)
        self.assertEqual(cafe_bill([I(50)], False), 54)

    def test_result_is_int(self):
        self.assertIs(type(cafe_bill([I(12345, 3)], True)), int)

    def test_reject_items(self):
        for bad in (None, [], (I(1),), [1], [{"price": 1}], [{"qty": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (1.5, 100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill([{"price": 100, "qty": bad}], False)

    def test_reject_member(self):
        for bad in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cafe_bill([I(100)], bad)

    def test_reject_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([I(100), I(100, 0)], False)


if __name__ == "__main__":
    unittest.main()
