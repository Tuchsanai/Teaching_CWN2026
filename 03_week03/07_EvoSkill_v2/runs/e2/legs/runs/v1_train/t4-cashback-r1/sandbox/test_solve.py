import unittest
from solve import cashback

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(50000, "platinum", True), 4000)
    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)
    def test_rounding(self):
        # 10010*0.015=150.15 ; 10033*0.015=150.495 ; 10100*.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertEqual(cashback(10010, "gold", False), 250)  # 250.25
        self.assertEqual(cashback(10020, "gold", False), 251)  # 250.5 -> 251
    def test_reject(self):
        for a in (-1, 100.0, "100", True, None):
            with self.assertRaises(ValueError): cashback(a, "gold", False)
        for t in ("bronze", None, ["gold"], 1):
            with self.assertRaises(ValueError): cashback(10000, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError): cashback(10000, "gold", b)
        with self.assertRaises(ValueError): cashback(-5, "x", 3)
        with self.assertRaises(ValueError): cashback(50, "bronze", False)

unittest.main() if __name__ == "__main__" else None
