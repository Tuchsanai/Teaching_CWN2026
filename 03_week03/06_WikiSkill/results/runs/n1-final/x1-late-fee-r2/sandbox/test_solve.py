import unittest
from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_boundary_below(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_boundary_at(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_half_up(self):
        # 4 days: 3% of 150 = 4.5 -> 5
        self.assertEqual(late_fee(150, 4), 5)
        # 10 days: 7.5% of 10 = 0.75 -> 1
        self.assertEqual(late_fee(10, 10), 1)
        # 4 days: 3% of 50 = 1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_reject_range(self):
        for a, d in [(-1, 5), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            late_fee(1000.0, 5)
        with self.assertRaises(ValueError):
            late_fee(1000, 5.0)

    def test_reject_bool_or_type(self):
        for a, d in [(True, 5), (100, False), ("100", 5), (100, None), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
