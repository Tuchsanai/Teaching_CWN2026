import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", True), 8000)
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "silver", True), 1500)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)

    def test_nodrift(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)     # 250.825
        self.assertEqual(cashback(10099, "gold", True), 504)      # 504.95

    def test_reject(self):
        bad = [(10000.0, "gold", False), ("10000", "gold", False), (True, "gold", False),
               (None, "gold", False), (-1, "gold", False), (10000, "bronze", False),
               (10000, None, False), (10000, "gold", 1), (10000, "gold", None),
               (5.5, "gold", False), (-1.5, "gold", False)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                cashback(*a)
        with self.assertRaises(ValueError):
            cashback(50, "x", False)  # ตรวจก่อน early-return


if __name__ == "__main__":
    unittest.main()
