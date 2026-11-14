import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_normal_2(self):
        self.assertEqual(late_fee(10000, 10), 750)

    def test_normal_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_3_days_free(self):
        self.assertEqual(late_fee(10000, 3), 0)

    def test_4_days(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_cap_reached_at_20(self):
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_cap_beyond(self):
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_zero_days(self):
        self.assertEqual(late_fee(10000, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half_rounds_up(self):
        self.assertEqual(late_fee(50, 4), 2)    # 1.5 -> 2
        self.assertEqual(late_fee(100, 10), 8)  # 7.5 -> 8

    def test_below_half(self):
        self.assertEqual(late_fee(1, 4), 0)     # 0.03 -> 0
        self.assertEqual(late_fee(1001, 4), 30)  # 30.03 -> 30


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)
        with self.assertRaises(ValueError):
            late_fee(100, 5.0)

    def test_str_none_bool(self):
        for a, d in [("100", 5), (100, "5"), (None, 5), (100, None), (True, 5), (100, True)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_range(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_validate_before_shortcut(self):
        with self.assertRaises(ValueError):
            late_fee(-5, 0)


if __name__ == "__main__":
    unittest.main()
