import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(250000, "gold", True), 12500)

    def test_nodrift(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)     # 250.825
        self.assertEqual(cashback(10033, "gold", True), 501)      # 501.65

    def test_reject(self):
        for a in (-1, 100.0, "100", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("Gold", "bronze", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)
        for b in (0, 1, "yes", None):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(-5, "gold", False)
        with self.assertRaises(ValueError):
            cashback(50, "x", False)


if __name__ == "__main__":
    unittest.main()
