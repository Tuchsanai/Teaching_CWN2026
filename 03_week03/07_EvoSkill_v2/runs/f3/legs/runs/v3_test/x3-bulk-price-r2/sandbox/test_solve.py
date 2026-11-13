import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(0, 1000, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(50, 1, False), 54)       # 53.5
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                     (100.0, 1, False), (100, 1.0, False), ("1", 1, False),
                     (True, 1, False), (100, True, False), (100, 1, 1),
                     (100, 1, None), (None, 1, False), (100, 1, "yes")]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
