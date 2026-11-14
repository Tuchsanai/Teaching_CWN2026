import unittest
from solve import bulk_price


class TestSolve(unittest.TestCase):
    def test_no_discount(self):
        # 1000*9*1.07 = 9630
        self.assertEqual(bulk_price(1000, 9, False), 9630)

    def test_tier1(self):
        # 10000*0.965*1.07 = 10325.5 -> half up 10326
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_tier2_coupon(self):
        # 50000*0.925*0.975*1.07 = 48250.3125 -> 48250
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_coupon_only(self):
        # 1000*0.975*1.07 = 1043.25 -> 1043
        self.assertEqual(bulk_price(1000, 1, True), 1043)

    def test_edge_9_vs_10(self):
        self.assertEqual(bulk_price(100, 9, False), 963)   # 900*1.07
        self.assertEqual(bulk_price(100, 10, False), 1033)  # 965*1.07=1032.55

    def test_edge_49_vs_50(self):
        # 4900*0.965*1.07=5059.4... -> 5059 ; 5000*0.925*1.07=4948.75 -> 4949
        self.assertEqual(bulk_price(100, 49, False), 5059)
        self.assertEqual(bulk_price(100, 50, False), 4949)

    def test_rounding_half_up(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # .5 exactly -> up
        self.assertEqual(bulk_price(100, 10, False), 1033)  # .55 -> up
        self.assertEqual(bulk_price(5, 1, False), 5)  # 5.35 -> 5
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07 -> 1

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_int_type(self):
        self.assertIs(type(bulk_price(333, 17, True)), int)

    def test_reject_unit_price(self):
        for v in (-1, 4500.0, True, "100", None):
            with self.assertRaises(ValueError):
                bulk_price(v, 1, False)

    def test_reject_qty(self):
        for v in (0, -1, 1001, 5.0, True, "3", None):
            with self.assertRaises(ValueError):
                bulk_price(100, v, False)

    def test_reject_coupon(self):
        for v in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                bulk_price(100, 1, v)


if __name__ == "__main__":
    unittest.main()
