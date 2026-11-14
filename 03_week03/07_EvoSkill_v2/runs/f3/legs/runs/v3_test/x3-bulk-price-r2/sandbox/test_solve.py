import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_single(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier10(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier50_coupon(self):
        # 462500*0.975=450937.5; *1.07=482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 472850*1.07=505949.5
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_zero_price_and_max_qty(self):
        self.assertEqual(bulk_price(0, 1, False), 0)
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(150, 1, False), 161)  # 160.5 -> 161

    def test_single_rounding(self):
        self.assertEqual(bulk_price(10000, 10, True), 100674)  # 100673.625


class Reject(unittest.TestCase):
    def test_float(self):
        for a in [(100.0, 1, False), (100, 1.0, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def test_str_none_bool(self):
        for a in [(100, "1", False), (None, 1, False), (True, 1, False), (100, True, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def test_range(self):
        for a in [(-1, 1, False), (100, 0, False), (100, 1001, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def test_coupon_type(self):
        for c in [1, 0, "yes", None]:
            with self.assertRaises(ValueError):
                bulk_price(100, 1, c)


if __name__ == "__main__":
    unittest.main()
