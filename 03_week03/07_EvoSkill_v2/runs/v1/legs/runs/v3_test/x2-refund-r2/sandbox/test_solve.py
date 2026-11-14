import unittest
from fractions import Fraction
from solve import refund


class Normal(unittest.TestCase):
    def test_a(self): self.assertEqual(refund(10000, 50, False), 5000)
    def test_b(self): self.assertEqual(refund(10000, 50, True), 4375)
    def test_c(self): self.assertEqual(refund(10000, 0, True), 8750)


class Boundary(unittest.TestCase):
    def test_80(self): self.assertEqual(refund(10000, 80, False), 2000)
    def test_81(self): self.assertEqual(refund(10000, 81, False), 0)
    def test_100(self): self.assertEqual(refund(10000, 100, True), 0)
    def test_zero_paid(self): self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        for paid in range(0, 300):
            for u in (0, 1, 33, 79, 80):
                for r in (False, True):
                    x = Fraction(paid * (100 - u), 100)
                    if r:
                        x *= Fraction(7, 8)
                    self.assertEqual(refund(paid, u, r), x.numerator // x.denominator)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 0, False), (10, -1, False), (10, 101, False), (1000.0, 0, False),
                  ("1000", 0, False), (True, 0, False), (10, 5.0, False), (10, True, False),
                  (10, 0, 1), (10, 0, "yes"), (None, 0, False), (10, 90, 1), (-5, 90, False)]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
