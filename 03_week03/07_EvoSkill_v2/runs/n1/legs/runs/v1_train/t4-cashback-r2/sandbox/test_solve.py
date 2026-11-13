import unittest
from fractions import Fraction
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)
        self.assertEqual(cashback(10**9, "gold", True), 20000)

    def test_nodrift(self):
        # 10033*0.015=150.495 ->150 ; 10034*.015=150.51 ->151
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5
        for a in range(10000, 10400):
            for t, r in (("silver", Fraction(3, 200)), ("gold", Fraction(1, 40)), ("platinum", Fraction(1, 25))):
                for b in (False, True):
                    v = a * r * (2 if b else 1)
                    exp = min(int((v * 2 + 1) // 2), 20000)
                    self.assertEqual(cashback(a, t, b), exp)
        self.assertIs(type(cashback(20000, "gold", True)), int)

    def test_reject(self):
        for args in [(-1, "gold", False), (100.0, "gold", False), ("100", "gold", False),
                     (True, "gold", False), (None, "gold", False), (20000, "bronze", False),
                     (20000, None, False), (20000, "gold", 1), (20000, "gold", "true"),
                     (20000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
