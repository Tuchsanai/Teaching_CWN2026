import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_no_fee(self):
        self.assertEqual(late_fee(100000, 0), 0)

    def test_normal_mid(self):
        # 10 วัน = 7.5% ของ 100000
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_normal_large(self):
        # 15 วัน = 11.25% ของ 200000
        self.assertEqual(late_fee(200000, 15), 22500)

    def test_edge_grace_3_days(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_edge_4_days(self):
        # เกิน 3 วัน นับรวม 3 วันแรก: 4 x 0.75% = 3%
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_edge_cap(self):
        # 19 วัน = 14.25% ; 20 วัน = 15% พอดี ; 21 วัน ติดเพดาน 15%
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_edge_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)

    def test_rounding(self):
        # 101 * 4 * 0.75% = 3.03 -> 3 ; 150*4*0.0075 = 4.5 -> 5 (ปัดครึ่งขึ้น)
        self.assertEqual(late_fee(101, 4), 3)
        self.assertEqual(late_fee(150, 4), 5)

    def test_result_is_int(self):
        self.assertIs(type(late_fee(12345, 7)), int)
        self.assertIs(type(late_fee(12345, 2)), int)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                late_fee(bad, 5)

    def test_reject_days_late(self):
        for bad in (-1, 366, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                late_fee(1000, bad)


if __name__ == "__main__":
    unittest.main()
