import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)  # 1000*1.07
        self.assertEqual(bulk_price(1000, 9, False), 9630)  # 9000*1.07

    def test_tier_10(self):
        self.assertEqual(bulk_price(1000, 20, False), 20651)  # 20000*.965*1.07=20651

    def test_tier_50(self):
        self.assertEqual(bulk_price(2000, 100, False), 197950)  # 200000*.925*1.07

    def test_coupon_only(self):
        self.assertEqual(bulk_price(1000, 1, True), 1043)  # 975*1.07=1043.25

    def test_coupon_tier10(self):
        self.assertEqual(bulk_price(1000, 10, True), 10067)  # 9650*.975*1.07=10067.06

    def test_coupon_tier50(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)  # 46250*.975*1.07=48250.31


class Boundary(unittest.TestCase):
    def test_around_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 9650*1.07=10325.5

    def test_around_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 47285*1.07=50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 46250*1.07=49487.5

    def test_extremes(self):
        self.assertEqual(bulk_price(0, 1, False), 0)
        self.assertEqual(bulk_price(0, 1000, True), 0)
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07
        self.assertEqual(bulk_price(1, 1000, False), 990)  # 925*1.07=989.75


class NoDrift(unittest.TestCase):
    def test_half_up_not_floor(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # .5 -> up
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # .5 -> up (even would give 49488 too)

    def test_half_up_not_even(self):
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54 (even gives 54)
        self.assertEqual(bulk_price(150, 1, False), 161)  # 160.5 -> 161 (even gives 160)

    def test_no_intermediate_rounding(self):
        # 333*10=3330*.965=3213.45*1.07=3438.3615 -> 3438
        self.assertEqual(bulk_price(333, 10, False), 3438)
        # 3330*.965*.975*1.07=3352.43 -> 3352
        self.assertEqual(bulk_price(333, 10, True), 3352)


class Reject(unittest.TestCase):
    def bad(self, *args):
        with self.assertRaises(ValueError):
            bulk_price(*args)

    def test_unit_price(self):
        for v in (1000.0, 10.5, "1000", True, None, -1):
            self.bad(v, 10, False)

    def test_qty(self):
        for v in (10.0, 10.5, "10", True, None, 0, -1, 1001):
            self.bad(1000, v, False)

    def test_coupon(self):
        for v in (0, 1, "yes", None, 1.0):
            self.bad(1000, 10, v)

    def test_invalid_even_when_other_branch(self):
        self.bad(0, 0, False)
        self.bad(0, 1, 1)


if __name__ == "__main__":
    unittest.main()
