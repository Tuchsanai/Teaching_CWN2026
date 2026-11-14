import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)
        self.assertEqual(cashback(20000, "platinum", True), 1600)
        self.assertEqual(cashback(20000, "silver", True), 300)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)     # 250.825
        self.assertEqual(cashback(10099, "gold", True), 504)      # 504.95


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in (-1, 1000.0, "1000", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", None, 1, "Gold"):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        for b in (0, 1, "True", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)


if __name__ == "__main__":
    unittest.main()
