import unittest
from fractions import Fraction
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_boundary(self):
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96
        self.assertEqual(cashback(499937, "platinum", False), 19997)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)

    def test_nodrift(self):
        # 10010*0.015 = 150.15 ; 10033*0.015=150.495 ; 10100*.025=252.5
        self.assertEqual(cashback(10100, "gold", False), 253)
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51
        for a in range(10000, 12000):
            for t, r in (("silver", Fraction(3, 200)), ("gold", Fraction(1, 40)), ("platinum", Fraction(1, 25))):
                for b in (False, True):
                    v = a * r * (2 if b else 1)
                    exp = min(int((v * 2 + 1) // 2), 20000)
                    got = cashback(a, t, b)
                    self.assertEqual(got, exp)
                    self.assertIs(type(got), int)

    def test_reject(self):
        bad = [(-1, "gold", False), (4500.0, "gold", False), ("3", "gold", False),
               (True, "gold", False), (None, "gold", False), (10000, "bronze", False),
               (10000, None, False), (10000, "gold", 1), (10000, "gold", "true"),
               (10000, "gold", None)]
        for args in bad:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
