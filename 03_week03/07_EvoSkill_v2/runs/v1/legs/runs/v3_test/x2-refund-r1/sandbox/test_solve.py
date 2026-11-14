import unittest
from fractions import Fraction
from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)

    def test_nodrift(self):
        for p in range(0, 400, 7):
            for u in (0, 33, 79, 80):
                for r in (True, False):
                    x = Fraction(p * (100 - u), 100) * (Fraction(7, 8) if r else 1)
                    self.assertEqual(refund(p, u, r), x.numerator // x.denominator)

    def test_reject(self):
        for a in [(-1, 0, False), (1, -1, False), (1, 101, False), (1.0, 0, False),
                  ("1", 0, False), (True, 0, False), (1, 1.0, False), (1, True, False),
                  (1, 0, 1), (1, 0, None), (None, 0, False)]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
