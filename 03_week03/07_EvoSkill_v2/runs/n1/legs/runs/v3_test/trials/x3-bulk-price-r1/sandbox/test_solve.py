"""python3 -m unittest -q test_solve"""
import unittest

from solve import bulk_price as f


class Normal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(f(10000, 1, False), 10700)

    def test_tier1(self):
        self.assertEqual(f(10000, 10, False), 103255)  # 100000*.965*1.07

    def test_tier2_coupon(self):
        self.assertEqual(f(10000, 50, True), 482503)  # 500000*.925*.975*1.07=482503.125

    def test_zero_price(self):
        self.assertEqual(f(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_9_10(self):
        self.assertEqual(f(1000, 9, False), 9630)
        self.assertEqual(f(1000, 10, False), 10326)  # 10000*.965*1.07=10325.5 -> half-up

    def test_49_50(self):
        self.assertEqual(f(1000, 49, False), 50595)  # 49000*.965*1.07=50594.95
        self.assertEqual(f(1000, 50, False), 49488)  # 50000*.925*1.07=49487.5

    def test_max(self):
        self.assertEqual(f(1000, 1000, False), 989750)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(f(1000, 10, False), 10326)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100.0, 1, False),
                     ("1", 1, False), (None, 1, False), (True, 1, False), (100, 1.0, False),
                     (100, "2", False), (100, True, False), (100, 1, 1), (100, 1, None), (100, 1, "yes")]:
            with self.assertRaises(ValueError, msg=str(args)):
                f(*args)


if __name__ == "__main__":
    unittest.main()
