import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier10_coupon(self):
        # 96500*.975*1.07 = 100674.125
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_tier50(self):
        # 500000*.925*1.07 = 494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)    # 9000*1.07
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 9650*1.07=10325.5

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 47285*1.07=50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 46250*1.07=49487.5

    def test_zero_and_max(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(100, 1000, False), 98975)  # 100000*.925*1.07


class NoDrift(unittest.TestCase):
    def test_half_rounds_up(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_single_rounding(self):
        # 10*.965*.975*1.07 = 10.067 -> 10
        self.assertEqual(bulk_price(1, 10, True), 10)
        # 1*1*.. coupon only: .975*1.07=1.04325 -> 1
        self.assertEqual(bulk_price(1, 1, True), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                  (100.0, 1, False), ("3", 1, False), (True, 1, False),
                  (100, 1.0, False), (100, True, False),
                  (100, 1, 1), (100, 1, None), (100, 1, "yes")]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
