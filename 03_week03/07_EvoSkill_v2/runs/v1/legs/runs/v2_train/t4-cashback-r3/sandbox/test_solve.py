import unittest
from solve import cashback


class Normal(unittest.TestCase):
    def test_basic(self):
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

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151 - 1)  # 150.51 -> floor 150
        self.assertEqual(cashback(10100, "gold", False), 252)    # 252.5 -> 252


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, "gold", False), (1000.0, "gold", False), ("1000", "gold", False),
               (True, "gold", False), (None, "gold", False),
               (10000, "bronze", False), (10000, "Gold", False), (10000, None, False),
               (10000, "gold", 1), (10000, "gold", "yes"), (5, "gold", None),
               (-5, "bronze", 0)]
        for a in bad:
            with self.assertRaises(ValueError, msg=repr(a)):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
