import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier1(self):
        # 10000*10*0.965*1.07 = 103255.0
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier2_coupon(self):
        # 500000*0.925*0.975*1.07 = 482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_coupon_only(self):
        # 10000*0.975*1.07 = 10432.5 -> half up
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_qty_limits(self):
        bulk_price(1, 1000, False)
        with self.assertRaises(ValueError):
            bulk_price(1, 1001, False)
        with self.assertRaises(ValueError):
            bulk_price(1, 0, False)


class NoDrift(unittest.TestCase):
    def test_half_up_not_bankers(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)
        self.assertEqual(bulk_price(1, 1, True), 1)  # 1.04325 -> 1


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, False), (100.0, 1, False), ("1", 1, False),
                     (True, 1, False), (None, 1, False), (100, 1.0, False),
                     (100, True, False), (100, "2", False), (100, 1, 1),
                     (100, 1, None), (100, 1, "yes")]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
