import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_tier1(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_tier2_with_coupon(self):
        # 500000*0.925*0.975*1.07 = 482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_normal_tier1_with_coupon(self):
        # 100000*0.965*0.975*1.07 = 100673.625 -> 100674
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_edge_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_edge_50(self):
        # ข้อสมมติ: ใช้อัตราเดียว 7.5% ที่ 50 ขึ้นไป ไม่ซ้อนกับ 3.5%
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_rounding(self):
        # 1000*0.965*1.07 = 1032.55 -> 1033 (ปัดครึ่งขึ้น/ปัดปกติ)
        self.assertEqual(bulk_price(100, 10, False), 1033)
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07 -> 1

    def test_returns_int(self):
        self.assertIs(type(bulk_price(1234, 12, True)), int)

    def test_reject_unit_price(self):
        for v in (-1, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                bulk_price(v, 1, False)

    def test_reject_qty(self):
        for v in (0, -1, 1001, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                bulk_price(100, v, False)

    def test_reject_coupon(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, v)

    def test_qty_bounds_ok(self):
        self.assertIs(type(bulk_price(100, 1, False)), int)
        self.assertEqual(bulk_price(100, 1000, False), 98975)  # 100000*0.925*1.07


if __name__ == "__main__":
    unittest.main()
