import unittest
from fractions import Fraction
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)   # 7.5%
        self.assertEqual(late_fee(200000, 4), 6000)    # 3%

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 200 * 4 * 0.0075 = 6.0 ; 50*4*0.0075=1.5 -> 2 ; 70*4*.0075=2.1 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(70, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)   # 0.3
        self.assertEqual(late_fee(30, 20), 5)  # 4.5 -> 5 (cap 15%)

    def test_matches_fraction(self):
        for a in (1, 33, 999, 12345):
            for d in (4, 7, 20, 30):
                x = Fraction(a) * min(Fraction(15, 100), Fraction(3, 400) * d)
                self.assertEqual(late_fee(a, d), (x * 2 + 1) // 2)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
