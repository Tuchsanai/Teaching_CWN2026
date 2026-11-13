import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # 20000 พอดี
        self.assertEqual(cashback(500000, "platinum", True), 20000)   # 40000 -> cap
        self.assertEqual(cashback(499900, "platinum", False), 19996)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(cashback(10020, "silver", True), 301)   # 300.6
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "gold", False), 251)    # 250.75
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5 -> 251


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, t, b in [(-1, "gold", False), (1.0, "gold", False), ("5", "gold", False),
                        (True, "gold", False), (None, "gold", False),
                        (20000, "bronze", False), (20000, None, False), (20000, ["x"], False),
                        (20000, "gold", 1), (20000, "gold", "yes"), (5, "bronze", False)]:
            with self.assertRaises(ValueError):
                cashback(a, t, b)


if __name__ == "__main__":
    unittest.main()
