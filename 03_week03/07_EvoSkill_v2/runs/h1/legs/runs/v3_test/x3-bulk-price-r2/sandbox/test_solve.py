import sys
import unittest
from fractions import Fraction

sys.path.insert(0, ".")
from solve import bulk_price, half_up  # noqa: E402


class BulkPrice(unittest.TestCase):
    def test_no_discount_below_10_no_coupon(self):
        # 9 ถุง * 100 สตางค์ = 900 * 1.07 = 963
        self.assertEqual(bulk_price(100, 9, False), 963)

    def test_tier_10_starts_at_10(self):
        # 10 ถุง * 10000 = 100000 * 0.965 * 1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        # 10 ถุง * 1 = 10 * 0.965 * 1.07 = 10.3255 -> 10
        self.assertEqual(bulk_price(1, 10, False), 10)

    def test_tier_50_starts_at_50(self):
        # 50 ถุง * 1 = 50 * 0.925 * 1.07 = 49.4875 -> 49
        self.assertEqual(bulk_price(1, 50, False), 49)
        # 49 ถุง * 100 = 4900 * 0.965 * 1.07 = 5059.3... -> 5059
        self.assertEqual(bulk_price(100, 49, False), 5059)

    def test_coupon_compounds_after_bulk(self):
        # 100000 * 0.965 * 0.975 * 1.07 = 100673.625 -> 100674
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 1000, True), 0)

    def test_max_qty(self):
        # 1000 * 500 = 500000 * 0.925 * 0.975 * 1.07, computed with Fraction
        expected = half_up(Fraction(500000) * Fraction(925, 1000) * Fraction(975, 1000) * Fraction(107, 100))
        self.assertEqual(bulk_price(500, 1000, True), expected)

    def test_qty_boundaries_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_unit_price_negative_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_wrong_types_rejected(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 10, False)
        with self.assertRaises(ValueError):
            bulk_price(True, 10, False)
        with self.assertRaises(ValueError):
            bulk_price(100, "10", False)
        with self.assertRaises(ValueError):
            bulk_price(100, 10, 1)
        with self.assertRaises(ValueError):
            bulk_price(100, 10, None)

    def test_half_up_helper(self):
        self.assertEqual(half_up(Fraction(5, 2)), 3)
        self.assertEqual(half_up(Fraction(7, 2)), 4)
        self.assertEqual(half_up(Fraction(49, 1)), 49)


if __name__ == "__main__":
    unittest.main()
