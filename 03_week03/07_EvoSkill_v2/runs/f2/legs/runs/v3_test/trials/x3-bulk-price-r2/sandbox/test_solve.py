import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 50, False), 494875)  # 500000*.925*1.07

    def test_coupon_stack(self):
        self.assertEqual(bulk_price(10000, 50, True), 482503)  # 482503.125
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 half up


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 half up

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_single_rounding(self):
        self.assertEqual(bulk_price(5, 1, False), 5)    # 5.35
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 half up


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, False), (10, 0, False), (10, 1001, False),
                     (10.0, 1, False), (10, 1.0, False), (10, True, False),
                     ("10", 1, False), (10, 1, 1), (10, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
