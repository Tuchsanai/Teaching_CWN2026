"""python3 -m unittest -q test_solve"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_gold(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_platinum(self):
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_gold_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_silver_birthday_no_bonus(self):  # C1
        self.assertEqual(cashback(20000, "silver", True), 300)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_on_min(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_cap_exact(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_over(self):
        self.assertEqual(cashback(600000, "platinum", True), 20000)

    def test_just_below_cap(self):
        self.assertEqual(cashback(499999, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_floor_silver(self):
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015

    def test_floor_half(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10040, "silver", False), 150)  # 150.6 -> floor

    def test_floor_gold_birthday(self):
        self.assertEqual(cashback(10001, "gold", True), 500)  # 500.05


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            cashback(*a)

    def test_amount(self):
        for v in (-1, 20000.0, "20000", None, True):
            self.bad(v, "gold", False)

    def test_tier(self):
        for v in ("bronze", "Gold", None, 1, ""):
            self.bad(20000, v, False)

    def test_birthday(self):
        for v in (0, 1, "yes", None):
            self.bad(20000, "gold", v)

    def test_invalid_even_if_below_min(self):
        self.bad(5, "bronze", False)


if __name__ == "__main__":
    unittest.main()
