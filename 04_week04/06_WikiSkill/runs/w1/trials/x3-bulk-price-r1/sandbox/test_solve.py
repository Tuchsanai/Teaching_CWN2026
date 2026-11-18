import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_tier1(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_tier2_with_coupon(self):
        # ลดตามจำนวนก่อน แล้วลดคูปองต่อ (คูณต่อเนื่อง) แล้วบวก VAT
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_normal_coupon_small_qty(self):
        # 10000*5*0.975*1.07 = 52162.5 -> ปัดครึ่งขึ้น
        self.assertEqual(bulk_price(10000, 5, True), 52163)

    def test_edge_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_edge_49_vs_50(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_edge_qty_limits(self):
        self.assertEqual(bulk_price(100, 1000, False), 98975)  # 100000*.925*1.07
        self.assertEqual(bulk_price(100, 1, False), 107)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(bulk_price(50, 1, False), 54)

    def test_rounding_once_at_end(self):
        # 3330*.965*.975*1.07 = 3352.5... รวมแล้วปัดครั้งเดียว
        self.assertEqual(bulk_price(333, 10, True), 3352)

    def test_result_is_int(self):
        self.assertIs(type(bulk_price(333, 10, True)), int)

    def test_reject_unit_price(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                bulk_price(bad, 1, False)

    def test_reject_qty(self):
        for bad in (0, -1, 1001, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                bulk_price(100, bad, False)

    def test_reject_coupon(self):
        for bad in (1, 0, "True", None, 1.0):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, bad)


if __name__ == "__main__":
    unittest.main()
