import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", True), 8000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_nodrift(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)     # 250.825
        self.assertEqual(cashback(10033, "silver", True), 300)    # 300.99

    def test_reject(self):
        for a in [(-1, "gold", False), (1.0, "gold", False), ("5", "gold", False),
                  (True, "gold", False), (20000, "bronze", False), (20000, None, False),
                  (20000, "gold", 1), (20000, "gold", "yes"), (5, "x", False)]:
            with self.assertRaises(ValueError):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
