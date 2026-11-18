import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([I(10000)], False), 10700)

    def test_member_only(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([I(10000)], True), 9630)

    def test_multiple_items(self):
        # 20000*2 + 10000 = 50000 -> *0.95*1.07 = 50825
        self.assertEqual(cafe_bill([I(20000, 2), I(10000)], False), 50825)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([I(50000)], False), 50825)

    def test_threshold_below(self):
        # 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill([I(49999)], False), 53499)

    def test_threshold_above(self):
        # 50001*0.95*1.07 = 50826.01
        self.assertEqual(cafe_bill([I(50001)], False), 50826)

    def test_both_discounts_rounding(self):
        # 50000*.95*.9*1.07 = 45742.5 -> ครึ่งขึ้น 45743
        self.assertEqual(cafe_bill([I(50000)], True), 45743)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([I(50)], False), 54)

    def test_returns_int(self):
        self.assertIs(type(cafe_bill([I(12345, 3)], True)), int)

    def test_reject_items(self):
        for bad in ([], None, "x", {}, [1], [{"price": 1}], [{"qty": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(100, bad)], False)

    def test_reject_member(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(100)], bad)

    def test_reject_bad_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([I(100), I(100, 0)], False)


if __name__ == "__main__":
    unittest.main()
