"""python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_10_days(self):
        self.assertEqual(late_fee(200000, 10), 15000)


class Boundary(unittest.TestCase):
    def test_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_0_days(self):
        self.assertEqual(late_fee(100000, 0), 0)

    def test_cap_exact_20(self):
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_below_cap_19(self):
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_over_cap(self):
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 66*0.0075*4 = 1.98 -> 2 ; 50*0.0075*4=1.5 -> 2 (half-up)
        self.assertEqual(late_fee(50, 4), 2)

    def test_below_half(self):
        self.assertEqual(late_fee(49, 4), 1)  # 1.47


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True),
                     (None, 5), (100, None)]:
            with self.subTest(a=a, d=d):
                with self.assertRaises(ValueError):
                    late_fee(a, d)

    def test_validate_even_when_free(self):
        with self.assertRaises(ValueError):
            late_fee(-5, 0)


if __name__ == "__main__":
    unittest.main()
