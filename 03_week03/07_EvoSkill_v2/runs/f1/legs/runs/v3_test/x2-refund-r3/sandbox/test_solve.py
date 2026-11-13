import unittest
from fractions import Fraction

from solve import refund as fn


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(fn(20000, 50, False), 10000)

    def test_restock(self):
        self.assertEqual(fn(20000, 50, True), 8750)

    def test_zero_used(self):
        self.assertEqual(fn(10000, 0, False), 10000)
        self.assertEqual(fn(10000, 0, True), 8750)

    def test_zero_paid(self):
        self.assertEqual(fn(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80_refunds(self):
        self.assertEqual(fn(10000, 80, False), 2000)
        self.assertEqual(fn(10000, 80, True), 1750)

    def test_79(self):
        self.assertEqual(fn(10000, 79, False), 2100)

    def test_81_zero(self):
        self.assertEqual(fn(10000, 81, False), 0)
        self.assertEqual(fn(10000, 81, True), 0)

    def test_100(self):
        self.assertEqual(fn(10000, 100, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_up_exact(self):
        # 10*50/100 = 5 -> *7/8 = 4.375 -> 4 ; 50 paid used 50 -> 25 *.875=21.875 -> 22
        self.assertEqual(fn(10, 50, True), 4)
        self.assertEqual(fn(50, 50, True), 22)

    def test_half_exact_up(self):
        # 1 * 50/100 = 0.5 -> 1
        self.assertEqual(fn(1, 50, False), 1)
        # 4 paid, 0 used, restock -> 3.5 -> 4
        self.assertEqual(fn(4, 0, True), 4)

    def test_below_half(self):
        self.assertEqual(fn(1, 51, False), 0)  # 0.49

    def test_matches_fraction(self):
        for paid in range(0, 400, 7):
            for u in (0, 13, 33, 80):
                for r in (False, True):
                    x = Fraction(paid * (100 - u), 100) * (Fraction(7, 8) if r else 1)
                    self.assertEqual(fn(paid, u, r), int((x * 2 + 1) // 2))


class Reject(unittest.TestCase):
    def test_reject_paid(self):
        for v in (-1, 1.0, "100", True, None):
            with self.subTest(v=v), self.assertRaises(ValueError):
                fn(v, 10, False)

    def test_reject_used(self):
        for v in (-1, 101, 10.0, "10", True, None):
            with self.subTest(v=v), self.assertRaises(ValueError):
                fn(100, v, False)

    def test_reject_restock(self):
        for v in (1, 0, "yes", None, 1.0):
            with self.subTest(v=v), self.assertRaises(ValueError):
                fn(100, 10, v)


if __name__ == "__main__":
    unittest.main()
