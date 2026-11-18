import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_small_delay(self):
        # 5 วัน: 10000*3.75% = 375
        self.assertEqual(late_fee(10000, 5), 375)

    def test_normal_ten_days(self):
        # 10 วัน: 20000*7.5% = 1500
        self.assertEqual(late_fee(20000, 10), 1500)

    def test_normal_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_edge_grace_period(self):
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(10000, 3), 0)

    def test_edge_first_day_over_grace(self):
        # 4 วัน: 10000*3% = 300 (นับรวม 3 วันแรก)
        self.assertEqual(late_fee(10000, 4), 300)

    def test_edge_cap_boundary(self):
        # 20 วัน = 15% พอดี; 19 วัน = 14.25%
        self.assertEqual(late_fee(10000, 19), 1425)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 21), 1500)

    def test_edge_max_days_capped(self):
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_rounding_half_up(self):
        # 200*4*0.75% = 6.0 ; 10*... 4 วัน amount=50 -> 1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        # amount=10, 4 วัน -> 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)

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
