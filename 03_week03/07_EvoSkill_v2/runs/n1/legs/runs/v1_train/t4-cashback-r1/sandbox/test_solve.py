import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(50000, "silver", False), 750)
        self.assertEqual(cashback(50000, "gold", False), 1250)
        self.assertEqual(cashback(50000, "platinum", True), 4000)

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
        bad = [(-1, "gold", False), (1.0, "gold", False), ("5", "gold", False),
               (True, "gold", False), (5000, "bronze", False), (5000, 1, False),
               (5000, "gold", 1), (5000, "gold", None), (5000, None, False)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
