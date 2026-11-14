import unittest
from fractions import Fraction
from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)

    def test_gold_birthday(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_platinum(self):
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_silver_no_birthday_bonus(self):
        self.assertEqual(cashback(100000, "silver", True), 1500)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        for amt in (10001, 10033, 12345, 99999, 123457):
            for t, r in (("silver", Fraction(3, 200)), ("gold", Fraction(1, 40)), ("platinum", Fraction(1, 25))):
                self.assertEqual(cashback(amt, t, False), min(20000, int((amt * r) // 1)))
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495 -> floor


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, "gold", False), (1000.0, "gold", False), ("1000", "gold", False),
               (True, "gold", False), (None, "gold", False), (10000, "bronze", False),
               (10000, "Gold", False), (10000, None, False), (10000, "gold", 1),
               (10000, "gold", "yes"), (5, "bronze", False), (float("nan"), "gold", False)]
        for a in bad:
            with self.subTest(a=a):
                with self.assertRaises(ValueError):
                    cashback(*a)


if __name__ == "__main__":
    unittest.main()
