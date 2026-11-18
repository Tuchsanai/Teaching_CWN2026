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
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_silver_no_birthday_bonus(self):  # C1
        self.assertEqual(cashback(20000, "silver", True), 300)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_on_min(self):
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)

    def test_just_below_cap(self):
        self.assertEqual(cashback(499999, "platinum", False), 19999)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10030, "gold", False), 250)     # 250.75 -> floor
        self.assertEqual(cashback(10010, "gold", True), 500)      # 500.5 -> floor


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [
            (-1, "gold", False), (20000.0, "gold", False), ("20000", "gold", False),
            (True, "gold", False), (None, "gold", False),
            (20000, "bronze", False), (20000, None, False), (20000, 1, False),
            (20000, "gold", 1), (20000, "gold", "yes"), (20000, "gold", None),
            (0, "gold", 0),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
