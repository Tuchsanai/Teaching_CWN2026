import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        # 10000*1.07 = 10700
        self.assertEqual(cafe_bill([I(10000)], False), 10700)

    def test_normal_member_only(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([I(10000)], True), 9630)

    def test_normal_multi_items(self):
        # 6000*2 + 5000*3 = 27000 -> *1.07 = 28890
        self.assertEqual(cafe_bill([I(6000, 2), I(5000, 3)], False), 28890)

    def test_big_and_member(self):
        # 100000*0.95*0.9*1.07 = 91485
        self.assertEqual(cafe_bill([I(100000)], True), 91485)

    def test_threshold_below(self):
        # 49999 ไม่ถึง 500 บาท: 49999*1.07=53498.93 -> 53499
        self.assertEqual(cafe_bill([I(49999)], False), 53499)

    def test_threshold_exact(self):
        # 50000 พอดี ลด 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([I(50000)], False), 50825)

    def test_threshold_above(self):
        # 50001*.95*1.07 = 50825.95 -> 50826
        self.assertEqual(cafe_bill([I(50001)], False), 50826)

    def test_threshold_by_qty(self):
        # 25000*2 = 50000 ได้ลด
        self.assertEqual(cafe_bill([I(25000, 2)], False), 50825)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54 (half-up)
        self.assertEqual(cafe_bill([I(50)], False), 54)

    def test_rounding_single_at_end(self):
        # 12345*.9*1.07 = 11888.4... -> 11888
        self.assertEqual(cafe_bill([I(12345)], True), 11888)

    def test_returns_int(self):
        self.assertIs(type(cafe_bill([I(12345)], True)), int)

    def test_reject_items(self):
        for bad in (None, [], "x", {}, [1], [{"price": 1}], [{"qty": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill([{"price": 100, "qty": bad}], False)

    def test_reject_member(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(100)], bad)

    def test_reject_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([I(100), I(100, 0)], False)


if __name__ == "__main__":
    unittest.main()
