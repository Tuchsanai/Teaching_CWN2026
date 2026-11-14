import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(50000, "silver", False), 750)
        self.assertEqual(cashback(50000, "gold", False), 1250)
        self.assertEqual(cashback(50000, "platinum", True), 4000)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "gold", False), 12500 if False else 12500)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_nodrift(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)     # 250.825
        self.assertIsInstance(cashback(12345, "gold", True), int)
        self.assertEqual(cashback(12345, "gold", True), 617)      # 617.25

    def test_reject(self):
        for a in (-1, 100.0, "100", True, None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("Gold", "bronze", None, 1):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        for b in (0, 1, "yes", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(5, "bad", False)


if __name__ == "__main__":
    unittest.main()
