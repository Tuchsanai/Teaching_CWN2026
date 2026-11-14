import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        # 10000*1*1.07 = 10700
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier1(self):
        # 10000*10*0.965*1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier2_coupon(self):
        # 462500*0.975=450937.5*1.07=482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_coupon_small_qty(self):
        # 10000*0.975*1.07 = 10432.5 -> half up 10433
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_edge_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)   # ไม่ลด
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # ลด 3.5%

    def test_edge_49_vs_50(self):
        # 49: 490000*.965=472850*1.07=505949.5 -> 505950 (ปัดครึ่งขึ้น)
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        # 50: 500000*.925=462500*1.07=494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54 ; 10*1.07=10.7 -> 11 ; 1*1.07 -> 1
        self.assertEqual(bulk_price(50, 1, False), 54)
        self.assertEqual(bulk_price(10, 1, False), 11)
        self.assertEqual(bulk_price(1, 1, False), 1)

    def test_returns_int(self):
        self.assertIs(type(bulk_price(123, 7, True)), int)

    def test_reject_unit_price(self):
        for bad in (-1, 10.0, True, "100", None):
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
