import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        # 10000 * 1.07 = 10700
        self.assertEqual(cafe_bill([it(10000)], False), 10700)

    def test_normal_member_only(self):
        # 10000*0.9=9000 *1.07 = 9630
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_normal_bulk_discount(self):
        # 60000*0.95=57000 *1.07 = 60990
        self.assertEqual(cafe_bill([it(60000)], False), 60990)

    def test_normal_bulk_and_member(self):
        # 60000*0.95*0.9=51300 *1.07 = 54891
        self.assertEqual(cafe_bill([it(60000)], True), 54891)

    def test_multiple_items_qty(self):
        # 12000*2 + 8000*3 = 48000 -> no bulk; *1.07 = 51360
        self.assertEqual(cafe_bill([it(12000, 2), it(8000, 3)], False), 51360)

    def test_edge_below_threshold(self):
        # 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([it(49999)], False), 53499)

    def test_edge_at_threshold(self):
        # ข้อสมมติ: ตั้งแต่ 500 บาท รวมพอดี -> 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_edge_above_threshold(self):
        # 50001*95*107/10000 = 50826.017 -> 50826
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_rounding_half_up_once(self):
        # 50 *1.07 = 53.5 -> 54 (ปัดครึ่งขึ้น)
        self.assertEqual(cafe_bill([it(50)], False), 54)
        # 1 *1.07 = 1.07 -> 1
        self.assertEqual(cafe_bill([it(1)], False), 1)

    def test_result_is_int(self):
        self.assertIs(type(cafe_bill([it(12345, 3)], True)), int)

    def test_reject_items(self):
        for bad in (None, (), "x", {}, [], [1], [{"price": 1}], [{"qty": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(100, bad)], False)

    def test_reject_member(self):
        for bad in (1, 0, "True", None, 1.0):
            with self.assertRaises(ValueError):
                cafe_bill([it(100)], bad)

    def test_reject_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100), it(100, 0)], False)


if __name__ == "__main__":
    unittest.main()
