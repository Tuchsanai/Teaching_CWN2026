import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(1000, 50, True), 48250)


class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        self.assertEqual(bulk_price(100, 1000, False), 98975)
        self.assertEqual(bulk_price(0, 1, True), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  (1, "3", False), (True, 1, False), (1, 1, 1), (1, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
