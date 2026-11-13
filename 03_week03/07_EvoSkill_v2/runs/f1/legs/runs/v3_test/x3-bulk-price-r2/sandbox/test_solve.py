import unittest
from solve import bulk_price as fn


class Normal(unittest.TestCase):
    def test_no_discount(self):  # 1000*5*1.07
        self.assertEqual(fn(1000, 5, False), 5350)

    def test_tier_10(self):  # 10000*.965*1.07 = 10325.5 -> 10325.5 -> 10326
        self.assertEqual(fn(1000, 10, False), 10326)

    def test_tier_50(self):  # 50000*.925*1.07 = 49487.5 -> 49488
        self.assertEqual(fn(1000, 50, False), 49488)

    def test_coupon(self):  # 5000*.975*1.07 = 5216.25
        self.assertEqual(fn(1000, 5, True), 5216)

    def test_tier_and_coupon(self):  # 50000*.925*.975*1.07 = 48250.3125
        self.assertEqual(fn(1000, 50, True), 48250)

    def test_zero_price(self):
        self.assertEqual(fn(0, 7, True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_10(self):
        self.assertEqual(fn(1000, 9, False), 9630)
        self.assertEqual(fn(1000, 10, False), 10326)
        self.assertEqual(fn(1000, 11, False), 11358)  # 11000*.965*1.07=11357.65

    def test_boundary_50(self):
        self.assertEqual(fn(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(fn(1000, 50, False), 49488)
        self.assertEqual(fn(1000, 51, False), 50477)  # 50477.25
    def test_range_ends(self):
        self.assertEqual(fn(1, 1, False), 1)
        self.assertEqual(fn(0, 1000, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # 49487.5 -> 49488
        self.assertEqual(fn(1000, 50, False), 49488)

    def test_below_half(self):  # 5216.25 -> 5216
        self.assertEqual(fn(1000, 5, True), 5216)

    def test_above_half(self):  # 50594.95 -> 50595
        self.assertEqual(fn(1000, 49, False), 50595)

    def test_fraction_multi_step(self):  # 48250.3125 -> 48250 (rounded once)
        self.assertEqual(fn(1000, 50, True), 48250)


class Reject(unittest.TestCase):
    def test_bad_values(self):
        bad = [
            (-1, 1, False), (1, 0, False), (1, 1001, False), (1, -1, False),
            (1.0, 1, False), (1, 1.0, False), ("1", 1, False), (1, "1", False),
            (True, 1, False), (1, True, False), (None, 1, False), (1, None, False),
            (1, 1, 1), (1, 1, 0), (1, 1, "yes"), (1, 1, None),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    fn(*args)

    def test_reject_unit_price(self):
        for v in (-1, 1.5, "100", True, None, [1]):
            with self.subTest(v=v):
                with self.assertRaises(ValueError):
                    fn(v, 1, False)

    def test_reject_qty(self):
        for v in (0, 1001, -5, 2.0, "2", True, None):
            with self.subTest(v=v):
                with self.assertRaises(ValueError):
                    fn(100, v, False)


if __name__ == "__main__":
    unittest.main()
