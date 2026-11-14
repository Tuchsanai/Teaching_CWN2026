import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_single(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier10(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier50(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_max_qty(self):
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)


class NoDrift(unittest.TestCase):
    def test_half_satang_coupon(self):
        # 10000*.975*1.07 = 10432.5 -> 10433
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_half_satang_tier(self):
        # 490000*.965*1.07 = 505949.5 -> 505950
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_stacked_not_added(self):
        # 100000*.925*.975*1.07 = 96496.875... -> 96503? computed by hand below
        # 500000*.925=462500; *.975=450937.5; *1.07=482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Reject(unittest.TestCase):
    def test_float_price(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)

    def test_str_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(100, "1", False)

    def test_bool_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(100, True, False)

    def test_qty_range(self):
        for q in (0, -1, 1001):
            with self.assertRaises(ValueError):
                bulk_price(100, q, False)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_coupon_not_bool(self):
        for c in (1, 0, "yes", None):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, c)


if __name__ == "__main__":
    unittest.main()
