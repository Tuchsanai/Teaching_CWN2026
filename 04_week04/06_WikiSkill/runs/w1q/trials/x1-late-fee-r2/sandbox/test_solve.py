import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_small_delay(self):
        # 4 วัน = 3% ของ 10000 = 300
        self.assertEqual(late_fee(10000, 4), 300)

    def test_normal_ten_days(self):
        # 10 วัน = 7.5% ของ 20000 = 1500
        self.assertEqual(late_fee(20000, 10), 1500)

    def test_normal_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_edge_grace_period(self):
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(10000, 3), 0)  # พอดี 3 วัน ไม่คิด

    def test_edge_first_charged_day(self):
        # วันที่ 4 คิดรวม 4 วัน (รวม 3 วันแรก)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_edge_cap(self):
        # 19 วัน = 14.25%, 20 วัน = 15% พอดี, 21 วัน ถูกจำกัดที่ 15%
        self.assertEqual(late_fee(10000, 19), 1425)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_rounding_half_up(self):
        # 1 สตางค์ * 20 วัน = 0.15 -> 0 ; 10 * 4 วัน = 0.3 -> 0
        self.assertEqual(late_fee(1, 20), 0)
        # 10 * 5 วัน = 0.375 -> 0 ; 14*4 = 0.42 -> 0 ; 17*4 = 0.51 -> 1
        self.assertEqual(late_fee(17, 4), 1)
        # 50*20 วัน=7.5 -> 8 (ครึ่งขึ้น)
        self.assertEqual(late_fee(50, 20), 8)

    def test_result_is_int(self):
        self.assertIs(type(late_fee(12345, 7)), int)
        self.assertIs(type(late_fee(12345, 2)), int)

    def test_reject_amount(self):
        for bad in (-1, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                late_fee(bad, 5)

    def test_reject_days_late(self):
        for bad in (-1, 366, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                late_fee(1000, bad)


if __name__ == "__main__":
    unittest.main()
