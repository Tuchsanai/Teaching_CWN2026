import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 ; 10030*0.015=150.45 ; 10033*.015=150.495
        self.assertEqual(cashback(10010, "silver", False), 150)
        # 10010*0.025=250.25; 10020*0.025=250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_reject(self):
        for a in (-1, 1.0, "1", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", None, 1, ["gold"]):
            with self.assertRaises(ValueError):
                cashback(100, t, False)
        with self.assertRaises(ValueError):
            cashback(5, "bronze", False)
        for b in (1, None, "x"):
            with self.assertRaises(ValueError):
                cashback(100, "gold", b)


if __name__ == "__main__":
    unittest.main()
