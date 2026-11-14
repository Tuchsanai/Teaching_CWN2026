import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        # 10000*1.07 = 10700
        self.assertEqual(cafe_bill([it(10000)], False), 10700)

    def test_member_only(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_multi_items_big_discount(self):
        # 20000*2 + 15000*4 = 100000 -> *0.95 = 95000 -> *1.07 = 101650
        self.assertEqual(cafe_bill([it(20000, 2), it(15000, 4)], False), 101650)

    def test_big_and_member(self):
        # 100000*0.95*0.9*1.07 = 91485
        self.assertEqual(cafe_bill([it(100000)], True), 91485)

    def test_edge_below_threshold(self):
        # 49999 ไม่ลด: 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([it(49999)], False), 53499)

    def test_edge_at_threshold(self):
        # 50000 พอดี (500 บาท) ลด 5%: 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_edge_above_threshold(self):
        # 50001*0.95*1.07 = 50826.01655 -> 50826
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54 (ปัดครึ่งขึ้น, ข้อสมมติ)
        self.assertEqual(cafe_bill([it(50)], False), 54)
        # 1*1.07 = 1.07 -> 1
        self.assertEqual(cafe_bill([it(1)], False), 1)

    def test_result_is_int(self):
        self.assertIs(type(cafe_bill([it(12345, 3)], True)), int)

    def test_reject_items(self):
        for bad in (None, "x", (it(1),), {"price": 1, "qty": 1}):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([1], False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1}], False)

    def test_reject_member(self):
        for bad in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cafe_bill([it(100)], bad)

    def test_reject_price(self):
        for bad in (100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(100, bad)], False)

    def test_reject_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100), it(100, 0)], False)


if __name__ == "__main__":
    unittest.main()
