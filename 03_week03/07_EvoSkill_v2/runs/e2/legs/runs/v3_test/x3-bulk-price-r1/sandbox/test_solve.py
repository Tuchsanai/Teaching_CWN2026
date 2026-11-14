import unittest
from fractions import Fraction
from solve import bulk_price


def ref(p, q, c):
    """อ้างอิงแยก: คำนวณมือด้วย Fraction"""
    r = Fraction(p * q)
    if q >= 50:
        r = r * 925 / 1000
    elif q >= 10:
        r = r * 965 / 1000
    if c:
        r = r * 975 / 1000
    r = r * 107 / 100
    return int((r * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(25075, 5, False), ref(25075, 5, False))

    def test_tier1(self):
        self.assertEqual(bulk_price(1000, 20, False), ref(1000, 20, False))
        self.assertEqual(bulk_price(5333, 30, True), ref(5333, 30, True))

    def test_tier2_single_rate(self):
        self.assertEqual(bulk_price(5001, 100, False), ref(5001, 100, False))
        self.assertEqual(bulk_price(5001, 100, True), ref(5001, 100, True))

    def test_coupon(self):
        self.assertEqual(bulk_price(1000, 1, True), 1043)  # 1000*.975*1.07=1043.25


class Boundary(unittest.TestCase):
    def test_qty_edges(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(5333, q, c), ref(5333, q, c))

    def test_tier_switch(self):
        self.assertLess(bulk_price(10000, 10, False), bulk_price(10000, 9, False) * 10 // 9 + 1)
        self.assertEqual(bulk_price(10000, 10, False), 103255 // 1 if False else ref(10000, 10, False))
        self.assertLess(bulk_price(10000, 50, False) / 50, bulk_price(10000, 49, False) / 49)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_exact(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5

    def test_half_up_vs_floor(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        self.assertEqual(bulk_price(1000, 10, True), 10067)  # 10067.3625

    def test_many(self):
        for p in (1, 7, 333, 5001, 25075):
            for q in (1, 3, 10, 13, 50, 77, 1000):
                for c in (False, True):
                    self.assertEqual(bulk_price(p, q, c), ref(p, q, c))


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            bulk_price(*a)

    def test_price(self):
        for v in (-1, 1000.0, "1000", True, None):
            self.bad(v, 5, False)

    def test_qty(self):
        for v in (0, -1, 1001, 5.0, "5", True, None):
            self.bad(1000, v, False)

    def test_coupon(self):
        for v in (0, 1, "True", None, 1.0):
            self.bad(1000, 5, v)


if __name__ == "__main__":
    unittest.main()
