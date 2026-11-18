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

    def test_multiple_items_qty(self):
        # 5000*2 + 3000*3 = 19000 -> 20330
        self.assertEqual(cafe_bill([I(5000, 2), I(3000, 3)], False), 20330)

    def test_exactly_500_baht(self):
        # ข้อสมมติ: พอดี 500 บาท ได้ลด 5% -> 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([I(50000)], False), 50825)

    def test_just_below_500(self):
        self.assertEqual(cafe_bill([I(49999)], False), 53499)

    def test_above_500_member(self):
        # 60000*.95*.9*1.07 = 54891
        self.assertEqual(cafe_bill([I(60000)], True), 54891)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([I(50)], False), 54)

    def test_returns_int(self):
        self.assertIs(type(cafe_bill([I(12345, 3)], True)), int)

    def test_reject_items(self):
        for bad in (None, "x", (I(1),), {"price": 1, "qty": 1}, [1], [{"price": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (10.0, True, "1", -1, None):
            with self.assertRaises(ValueError):
                cafe_bill([I(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1"):
            with self.assertRaises(ValueError):
                cafe_bill([I(100, bad)], False)

    def test_reject_member(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cafe_bill([I(100)], bad)


if __name__ == "__main__":
    unittest.main()
