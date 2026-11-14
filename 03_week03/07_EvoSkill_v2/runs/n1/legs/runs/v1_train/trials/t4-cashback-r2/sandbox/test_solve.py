"""python3 -m unittest -q test_solve"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_silver_no_birthday_bonus(self):  # นโยบาย C1
        self.assertEqual(cashback(20000, "silver", True), 300)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 150)   # 150.51 ปัดลง
        self.assertEqual(cashback(10030, "silver", False), 150)   # 150.45 (ไม่ปัดขึ้น)
        self.assertEqual(cashback(10020, "gold", False), 250)     # 250.5 -> 250


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, "gold", False), (20000.0, "gold", False), ("2", "gold", False),
               (True, "gold", False), (None, "gold", False),
               (20000, "bronze", False), (20000, None, False), (20000, "Gold", False),
               (20000, "gold", 1), (20000, "gold", None), (20000, "gold", "yes"),
               (5, "bogus", False), (5, "gold", 0)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
