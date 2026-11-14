"""python3 -m unittest -q test_solve"""
import unittest
from fractions import Fraction

from solve import bulk_price, half_up


def ref(p, q, c):
    a = Fraction(p * q)
    a *= Fraction(925, 1000) if q >= 50 else Fraction(965, 1000) if q >= 10 else 1
    if c:
        a *= Fraction(975, 1000)
    return half_up(a * Fraction(107, 100))


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_coupon_only(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 -> half-up

    def test_tier1(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 103255.0

    def test_tier2_coupon(self):
        self.assertEqual(bulk_price(10000, 50, True), 482503)  # 482503.125


class Boundary(unittest.TestCase):
    def test_lines(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(1234, q, c), ref(1234, q, c))

    def test_9_vs_10(self):
        self.assertLess(bulk_price(10000, 10, False) / 10, bulk_price(10000, 9, False) / 9)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_many(self):
        for p in range(0, 400, 7):
            for q in (1, 10, 50, 77):
                self.assertEqual(bulk_price(p, q, True), ref(p, q, True))


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            bulk_price(*a)

    def test_price(self):
        for v in (-1, 4500.0, "1", None, True):
            self.bad(v, 1, False)

    def test_qty(self):
        for v in (0, -1, 1001, 1.0, "2", None, True):
            self.bad(100, v, False)

    def test_coupon(self):
        for v in (0, 1, "yes", None):
            self.bad(100, 1, v)


if __name__ == "__main__":
    unittest.main()
