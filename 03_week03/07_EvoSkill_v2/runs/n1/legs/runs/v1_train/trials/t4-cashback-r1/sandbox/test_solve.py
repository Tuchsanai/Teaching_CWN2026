"""python3 -m unittest -q test_solve"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_gold(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_gold_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_silver_birthday_no_bonus(self):
        self.assertEqual(cashback(20000, "silver", True), 300)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)     # 250.825
        self.assertEqual(cashback(10010, "gold", True), 500)      # 500.5


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, "gold", False), (100.0, "gold", False), ("100", "gold", False),
                     (True, "gold", False), (None, "gold", False), (20000, "bronze", False),
                     (20000, None, False), (20000, "gold", 1), (20000, "gold", None),
                     (0, "x", False), (5, "gold", "yes")]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
