import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(100, 50, True), 4825)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(100, 9, False), 963)
        self.assertEqual(bulk_price(100, 10, False), 1033)   # 965*1.07=1032.55
        self.assertEqual(bulk_price(100, 49, False), 5059)
        self.assertEqual(bulk_price(100, 50, False), 4949)
        self.assertEqual(bulk_price(0, 5, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> up


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(100.0, 1, False), ("1", 1, False), (-1, 1, False), (True, 1, False),
                  (100, 0, False), (100, 1001, False), (100, 1.0, False), (100, True, False),
                  (100, 1, 1), (100, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
