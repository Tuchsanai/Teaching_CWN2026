import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        # 10000*1*1.07
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_coupon_only(self):
        # 10000*0.975*1.07 = 10432.5 -> 10433 (ครึ่งขึ้น)
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_normal_tier1(self):
        # 100000*0.965*1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_tier2_with_coupon(self):
        # 500000*0.925*0.975*1.07 = 482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_normal_max_qty(self):
        # 10,000,000*0.925*0.975*1.07 = 9650062.5 -> 9650063
        self.assertEqual(bulk_price(10000, 1000, True), 9650063)

    def test_edge_qty_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)   # ไม่ลด
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # ลด 3.5%

    def test_edge_qty_49_vs_50(self):
        # 490000*0.965*1.07 = 505949.5 -> 505950
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        # 500000*0.925*1.07 = 494875 (อัตราเดียว ไม่ซ้อนกับ 3.5%)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_edge_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_rounding(self):
        # สมมติ: ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
        self.assertEqual(bulk_price(1, 1, False), 1)    # 1.07
        self.assertEqual(bulk_price(5, 1, False), 5)    # 5.35
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5

    def test_result_is_int(self):
        self.assertIs(type(bulk_price(12345, 7, True)), int)

    def test_reject_unit_price(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                bulk_price(bad, 1, False)

    def test_reject_qty(self):
        for bad in (0, -1, 1001, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                bulk_price(100, bad, False)

    def test_reject_coupon(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, bad)


if __name__ == "__main__":
    unittest.main()
