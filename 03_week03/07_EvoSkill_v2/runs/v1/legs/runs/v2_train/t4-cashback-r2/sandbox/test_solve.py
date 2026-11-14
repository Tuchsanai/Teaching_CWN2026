import unittest
from fractions import Fraction
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
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        for a in (10001, 12345, 33333, 99999):
            for t, r in (("silver", Fraction(3, 200)), ("gold", Fraction(1, 40)), ("platinum", Fraction(1, 25))):
                self.assertEqual(cashback(a, t, False), int(a * r // 1))
        self.assertEqual(cashback(10001, "silver", False), 150)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False), ("1000", "gold", False),
                     (True, "gold", False), (None, "gold", False), (20000, "bronze", False),
                     (20000, "Gold", False), (20000, None, False), (20000, "gold", 1),
                     (20000, "gold", "yes"), (20000, "gold", None), (50, "gold", 1)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
