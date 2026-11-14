import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)  # 4*0.75% = 3%

    def test_10_days(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_0_days(self):
        self.assertEqual(late_fee(100000, 0), 0)

    def test_cap_19(self):
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_cap_20(self):
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_cap_21_and_max(self):
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up_exact_half(self):
        self.assertEqual(late_fee(40, 5), 2)  # 1.5 -> 2

    def test_round_down_below_half(self):
        self.assertEqual(late_fee(10, 5), 0)  # 0.375 -> 0

    def test_round_up(self):
        self.assertEqual(late_fee(50, 10), 4)  # 3.75 -> 4

    def test_no_float_error(self):
        self.assertEqual(late_fee(10**12, 4), 3 * 10**10)


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)
        with self.assertRaises(ValueError):
            late_fee(100, 5.0)

    def test_str_none(self):
        with self.assertRaises(ValueError):
            late_fee("100", 5)
        with self.assertRaises(ValueError):
            late_fee(100, None)

    def test_bool(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)
        with self.assertRaises(ValueError):
            late_fee(100, True)

    def test_range(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_validate_before_shortcut(self):
        with self.assertRaises(ValueError):
            late_fee(-5, 0)


if __name__ == "__main__":
    unittest.main()
