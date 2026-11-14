import unittest
from fractions import Fraction
from solve import refund


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80_81(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)
        self.assertEqual(refund(10000, 100, False), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        for paid in (1, 7, 99, 12345, 99999):
            for u in (0, 1, 33, 80):
                for r in (False, True):
                    x = Fraction(paid * (100 - u), 100)
                    if r:
                        x *= Fraction(875, 1000)
                    self.assertEqual(refund(paid, u, r), x.numerator // x.denominator)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 10, True), (100, -1, True), (100, 101, True),
               (100.0, 10, True), ("100", 10, True), (True, 10, True),
               (100, 10.0, True), (100, True, True), (100, 10, 1),
               (100, 10, "yes"), (None, 10, True)]
        for a in bad:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
