import unittest

from solve import bulk_price as fn


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(fn(10000, 1, False), 10700)

    def test_tier10(self):
        self.assertEqual(fn(10000, 10, False), 103255)

    def test_tier50_coupon(self):
        self.assertEqual(fn(10000, 50, True), 482503)

    def test_max(self):
        self.assertEqual(fn(1000, 1000, True), 965006)

    def test_zero_price(self):
        self.assertEqual(fn(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_10(self):
        self.assertEqual(fn(333, 9, False), 3207)
        self.assertEqual(fn(333, 10, False), 3438)

    def test_boundary_50(self):
        self.assertEqual(fn(333, 49, True), 16427)
        self.assertEqual(fn(333, 50, False), 16479)

    def test_qty_limits(self):
        self.assertEqual(fn(1, 1, False), 1)
        self.assertIsInstance(fn(1000, 1000, False), int)


class NoDrift(unittest.TestCase):
    def test_half_up_exact(self):  # 10432.5 -> 10433
        self.assertEqual(fn(10000, 1, True), 10433)

    def test_below_half(self):  # 320.679 -> 3207 (>.5) ; 107/100 -> 1
        self.assertEqual(fn(1, 1, False), 1)

    def test_multi_step(self):  # 4173/800 = 5.216 -> 5
        self.assertEqual(fn(5, 1, True), 5)


class Reject(unittest.TestCase):
    def _bad(self, *a):
        with self.assertRaises(ValueError):
            fn(*a)

    def test_reject_price(self):
        for v in (-1, 1.0, "100", True, None):
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
