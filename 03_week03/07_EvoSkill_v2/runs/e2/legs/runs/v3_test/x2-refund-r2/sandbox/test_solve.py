import unittest
from fractions import Fraction
from solve import refund


def manual(paid, u, r):
    v = Fraction(paid * (100 - u), 100)
    if r:
        v = v * 7 / 8
    return v.numerator // v.denominator


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(100000, 50, False), 50000)
        self.assertEqual(refund(100000, 50, True), 43750)
        self.assertEqual(refund(100000, 0, False), 100000)
        self.assertEqual(refund(100000, 0, True), 87500)
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 79, False), 2100)
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)
        self.assertEqual(refund(10000, 100, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        # 5001*50/100 = 2500.5 -> 2500
        self.assertEqual(refund(5001, 50, False), 2500)
        # 5001*.5*.875 = 2187.9375 -> 2187
        self.assertEqual(refund(5001, 50, True), 2187)
        # 1*0.875 -> 0 ; 3*.875=2.625 -> 2
        self.assertEqual(refund(1, 0, True), 0)
        self.assertEqual(refund(3, 0, True), 2)
        # 4 * 0.875 = 3.5 -> 3 (floor, not half-up)
        self.assertEqual(refund(4, 0, True), 3)

    def test_sweep(self):
        for p in (1, 7, 333, 5001, 25075, 99999):
            for u in range(0, 101):
                for r in (False, True):
                    exp = 0 if u > 80 else manual(p, u, r)
                    self.assertEqual(refund(p, u, r), exp)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)

    def test_paid(self):
        for v in (-1, 1000.0, "1000", True, None):
            self.bad(v, 10, False)

    def test_used(self):
        for v in (-1, 101, 10.0, "10", True, False, None):
            self.bad(1000, v, False)

    def test_restock(self):
        for v in (0, 1, "True", None, 1.0):
            self.bad(1000, 10, v)

    def test_order(self):
        self.bad(1000, 101, True)
        self.bad(-5, 90, False)


if __name__ == "__main__":
    unittest.main()
