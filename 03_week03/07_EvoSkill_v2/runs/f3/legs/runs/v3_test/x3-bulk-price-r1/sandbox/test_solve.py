import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_single(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_ten_no_coupon(self):  # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_fifty_coupon(self):  # 500000*.925*.975*1.07 = 482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 9650*1.07=10325.5

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 49000*.965*1.07=50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 46250*1.07=49487.5

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54

    def test_coupon_half(self):
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(100.0, 1, False), (100, "1", False), (100, 1, 1), (-1, 1, False),
                     (100, 0, False), (100, 1001, False), (True, 1, False), (100, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
