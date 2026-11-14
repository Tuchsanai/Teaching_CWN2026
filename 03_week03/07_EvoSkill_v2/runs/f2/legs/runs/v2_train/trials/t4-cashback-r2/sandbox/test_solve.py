import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_rates(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "platinum", True), 8000)
        self.assertEqual(cashback(100000, "silver", True), 1500)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)  # 250.825


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, "gold", False), (100.0, "gold", False), ("1", "gold", False),
                  (True, "gold", False), (100, "bronze", False), (100, None, False),
                  (100, "gold", 1), (50, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
