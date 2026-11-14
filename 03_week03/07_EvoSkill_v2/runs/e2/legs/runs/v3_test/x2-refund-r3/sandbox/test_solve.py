import unittest
from fractions import Fraction

from solve import refund


def expected(paid, used, restock):
    if used > 80:
        return 0
    v = Fraction(paid * (100 - used), 100)
    if restock:
        v = v * Fraction(7, 8)
    return v.numerator // v.denominator


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)
        self.assertEqual(refund(0, 10, False), 0)


class Boundary(unittest.TestCase):
    def test_80_81(self):
        self.assertEqual(refund(10000, 79, False), 2100)
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 80, True), 1750)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_extremes(self):
        self.assertEqual(refund(10000, 100, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(5001, 0, False), 5001)


class NoDrift(unittest.TestCase):
    def test_exact_half(self):
        # 1*(50)/100*7/8 = 0.4375 -> 0 ; 4 * 75/100 = 3 -> *7/8 = 2.625 -> 2
        self.assertEqual(refund(4, 25, True), 2)
        # 1 * 50/100 = 0.5 -> floor 0 (ไม่ปัดขึ้น)
        self.assertEqual(refund(1, 50, False), 0)
        # 3 * 50/100 = 1.5 -> 1
        self.assertEqual(refund(3, 50, False), 1)

    def test_floor_vs_round(self):
        # 5333*0.8*0.875 = 3733.1 ; 5001*0.9*0.875=3938.2875
        self.assertEqual(refund(5333, 20, True), expected(5333, 20, True))
        self.assertEqual(refund(5001, 10, True), 3938)
        # 25075 * 0.67 = 16800.25 ; *0.875 = 14700.21875
        self.assertEqual(refund(25075, 33, False), 16800)
        self.assertEqual(refund(25075, 33, True), 14700)

    def test_many(self):
        for p in (1, 7, 99, 5001, 5333, 25075, 123457):
            for u in range(0, 101):
                for r in (False, True):
                    self.assertEqual(refund(p, u, r), expected(p, u, r))


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)

    def test_paid(self):
        for v in (-1, 1000.0, "1000", True, None, [1]):
            self.bad(v, 10, False)

    def test_used(self):
        for v in (-1, 101, 10.0, "10", True, False, None):
            self.bad(1000, v, False)

    def test_restock(self):
        for v in (0, 1, "True", None, 1.0):
            self.bad(1000, 10, v)

    def test_reject_before_shortcut(self):
        self.bad(1000, 101, True)
        self.bad(-5, 90, False)


if __name__ == "__main__":
    unittest.main()
