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

    def test_birthday_gold(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_birthday_platinum(self):
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_birthday_silver_no_bonus(self):  # C1
        self.assertEqual(cashback(20000, "silver", True), 300)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_on_min(self):
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_cap_exact(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_over(self):
        self.assertEqual(cashback(300000, "platinum", True), 20000)

    def test_just_under_cap(self):
        self.assertEqual(cashback(499999, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        self.assertEqual(cashback(10100, "silver", False), 151)  # 151.5
        self.assertEqual(cashback(10020, "gold", False), 250)    # 250.5

    def test_floor_51(self):
        self.assertEqual(cashback(10034, "silver", False), 150)  # 150.51

    def test_floor_49(self):
        self.assertEqual(cashback(10032, "silver", False), 150)  # 150.48


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

    def test_checked_even_below_min(self):
        self.bad(0, "bronze", False)
        self.bad(5, "gold", 1)


if __name__ == "__main__":
    unittest.main()
