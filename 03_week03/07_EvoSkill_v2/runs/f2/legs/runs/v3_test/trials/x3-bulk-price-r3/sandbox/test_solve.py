import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 half-up
    def test_zero(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_int(self):
        self.assertIsInstance(bulk_price(333, 49, True), int)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  (1, True, False), (1, 1, 1), ("1", 1, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
