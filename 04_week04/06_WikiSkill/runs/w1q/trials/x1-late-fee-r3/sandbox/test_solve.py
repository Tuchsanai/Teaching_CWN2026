import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_ten_days(self):
        # 10000 * 0.75% * 10 = 750
        self.assertEqual(late_fee(10000, 10), 750)

    def test_normal_four_days(self):
        # 20000 * 0.0075 * 4 = 600
        self.assertEqual(late_fee(20000, 4), 600)

    def test_normal_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_edge_exactly_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_edge_4_days_counts_all_days(self):
        # นับรวม 3 วันแรก: 100000*0.0075*4 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_edge_below_3_days(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 2), 0)

    def test_edge_cap_at_20_days(self):
        # 20 วัน = 15% พอดี, 19 วัน = 14.25%
        self.assertEqual(late_fee(10000, 19), 1425)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 21), 1500)

    def test_edge_cap_max_days(self):
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_rounding_half_up(self):
        # 100*0.0075*4 = 3.0 ; 150*0.0075*4 = 4.5 -> 5 (ข้อสมมติ: ปัดครึ่งขึ้น)
        self.assertEqual(late_fee(100, 4), 3)
        self.assertEqual(late_fee(150, 4), 5)
        # 10*0.0075*4 = 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)

    def test_result_is_int(self):
        self.assertIs(type(late_fee(12345, 7)), int)
        self.assertIs(type(late_fee(12345, 1)), int)

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
