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
        self.assertEqual(cashback(0, "silver", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)

    def test_floor(self):
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10039, "gold", False), 250)     # 250.975
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_reject(self):
        for a in (-1, 1.0, 20000.0, "3", None, True):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "Gold", None, 1):
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(5, "bad", False)


if __name__ == "__main__":
    unittest.main()
