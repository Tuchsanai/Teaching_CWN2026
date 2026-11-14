import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier_10(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier_50_with_coupon(self):
        # 500000*.925*.975*1.07 = 482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_edge_below_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_edge_below_50(self):
        # 472850*1.07 = 505949.5 -> ปัดขึ้น (half up: ข้อสมมติ)
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_edge_exact_50_not_stacked(self):
        # 50 ใช้ 7.5% อัตราเดียว ไม่ซ้อน 3.5%
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_rounding_coupon(self):
        # 9750*1.07 = 10432.5 -> 10433
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_result_is_int(self):
        self.assertIs(type(bulk_price(333, 7, True)), int)

    def test_reject_unit_price(self):
        for v in (-1, 100.0, True, "100", None):
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


if __name__ == "__main__":
    unittest.main()
