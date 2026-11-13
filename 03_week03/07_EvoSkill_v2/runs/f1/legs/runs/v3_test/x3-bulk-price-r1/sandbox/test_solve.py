import unittest
from fractions import Fraction as F

from solve import bulk_price as fn


def ref(p, q, c):
    x = F(p) * q
    if q >= 50:
        x *= F(925, 1000)
    elif q >= 10:
        x *= F(965, 1000)
    if c:
        x *= F(975, 1000)
    x *= F(107, 100)
    return int((x * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(fn(10000, 1, False), 10700)

    def test_tier_10(self):
        self.assertEqual(fn(10000, 10, False), 103255)

    def test_tier_50(self):
        self.assertEqual(fn(10000, 50, False), 494875)

    def test_coupon(self):
        self.assertEqual(fn(10000, 1, True), 10433)  # 10432.5 up

    def test_tier_and_coupon(self):
        self.assertEqual(fn(10000, 50, True), 482503)  # 482503.125

    def test_zero_price(self):
        self.assertEqual(fn(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_qty_9_10_11(self):
        self.assertEqual(fn(1000, 9, False), 9630)
        self.assertEqual(fn(1000, 10, False), 10326)
        self.assertEqual(fn(1000, 11, False), 11358)

    def test_qty_49_50_51(self):
        self.assertEqual(fn(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(fn(1000, 50, False), 49488)
        self.assertEqual(fn(1000, 51, False), 50477)  # 50477.25

    def test_range_edges(self):
        self.assertEqual(fn(1, 1, False), 1)
        self.assertEqual(fn(100, 1000, False), 98975)  # 92500*1.07


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(1000, 10, False), 10326)  # .5

    def test_below_half(self):
        self.assertEqual(fn(1001, 1, False), 1071)  # 1071.07

    def test_above_half(self):
        self.assertEqual(fn(15, 1, False), 16)  # 16.05
        self.assertEqual(fn(1, 10, False), 10)  # 10.3255

    def test_multi_step(self):
        for p in (1, 7, 333, 9999, 123457):
            for q in (1, 10, 50, 999):
                for c in (False, True):
                    self.assertEqual(fn(p, q, c), ref(p, q, c))


class Reject(unittest.TestCase):
    def _bad(self, *a):
        with self.assertRaises(ValueError):
            fn(*a)

    def test_reject_price(self):
        for v in (-1, 1.0, "100", True, None, [1]):
            with self.subTest(v=v):
                self._bad(v, 1, False)

    def test_reject_qty(self):
        for v in (0, -1, 1001, 1.0, "1", True, None):
            with self.subTest(v=v):
                self._bad(100, v, False)

    def test_reject_coupon(self):
        for v in (1, 0, "yes", None, 1.0):
            with self.subTest(v=v):
                self._bad(100, 1, v)


if __name__ == "__main__":
    unittest.main()
