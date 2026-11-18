"""python3 -m unittest -q test_solve"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_gold(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_platinum(self):
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_gold_birthday(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(50000, "platinum", True), 4000)

    def test_silver_birthday_no_bonus(self):
        self.assertEqual(cashback(10000, "silver", True), 150)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_on_min(self):
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_cap_exact(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_over(self):
        self.assertEqual(cashback(1000000, "platinum", True), 20000)

    def test_just_below_cap(self):
        self.assertEqual(cashback(499975, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        # 10001 * 0.015 = 150.015 -> 150
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_floor_high(self):
        # 10033 * 0.025 = 250.825 -> 250 (ไม่ใช่ 251)
        self.assertEqual(cashback(10033, "gold", False), 250)

    def test_floor_exact_half(self):
        # 10010 * 0.015 = 150.15 ; 10030*0.025=250.75 ; 10020*0.025=250.5 -> 250
        self.assertEqual(cashback(10020, "gold", False), 250)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            cashback(*a)

    def test_amount(self):
        for v in (-1, 10000.0, "10000", True, None):
            self.bad(v, "gold", False)

    def test_tier(self):
        for v in ("bronze", "Gold", None, 1, ""):
            self.bad(10000, v, False)

    def test_birthday(self):
        for v in (0, 1, "yes", None):
            self.bad(10000, "gold", v)

    def test_checked_even_if_small(self):
        self.bad(0, "bronze", False)
        self.bad(5, "gold", 1)


if __name__ == "__main__":
    unittest.main()
