import unittest

from solve import late_fee


class LateFeeValues(unittest.TestCase):
    # ค่าที่คำนวณมือไว้ก่อน (ดูคอมเมนต์แต่ละกรณี)

    def test_grace_period_no_fee(self):
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(10000, 1), 0)
        self.assertEqual(late_fee(10000, 2), 0)
        self.assertEqual(late_fee(10000, 3), 0)   # เกณฑ์พอดี ยังไม่คิด

    def test_first_charged_day(self):
        # 10000 * 0.75% * 4 = 300
        self.assertEqual(late_fee(10000, 4), 300)

    def test_counts_all_days_including_first_three(self):
        # 10000 * 0.75% * 10 = 750
        self.assertEqual(late_fee(10000, 10), 750)

    def test_half_up_not_bankers(self):
        # 150 * 0.75% * 4 = 4.5 -> 5 (banker's round จะได้ 4)
        self.assertEqual(late_fee(150, 4), 5)
        # 50 * 0.75% * 4 = 1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)

    def test_rounds_down_below_half(self):
        # 1 * 0.75% * 4 = 0.03 -> 0
        self.assertEqual(late_fee(1, 4), 0)
        # 67 * 0.75% * 4 = 2.01 -> 2
        self.assertEqual(late_fee(67, 4), 2)

    def test_cap_boundary_at_20_days(self):
        # 10000 * 0.75% * 19 = 1425 (ยังไม่ถึงเพดาน 1500)
        self.assertEqual(late_fee(10000, 19), 1425)
        # 10000 * 0.75% * 20 = 1500 = เพดานพอดี
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_cap_applies_after(self):
        self.assertEqual(late_fee(10000, 21), 1500)   # raw 1575 -> เพดาน 1500
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 0), 0)
        self.assertEqual(late_fee(0, 365), 0)

    def test_returns_int(self):
        self.assertIs(type(late_fee(10000, 4)), int)
        self.assertIs(type(late_fee(10000, 0)), int)


class LateFeeRejects(unittest.TestCase):
    def test_amount_float_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 4)

    def test_amount_negative_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 4)

    def test_amount_str_rejected(self):
        with self.assertRaises(ValueError):
            late_fee("100", 4)

    def test_amount_bool_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(True, 4)

    def test_days_float_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(100, 4.0)

    def test_days_bool_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(100, True)

    def test_days_str_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(100, "4")

    def test_days_negative_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(100, -1)

    def test_days_over_365_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(100, 366)

    def test_days_365_accepted(self):
        self.assertEqual(late_fee(100, 365), 15)


if __name__ == "__main__":
    unittest.main()
