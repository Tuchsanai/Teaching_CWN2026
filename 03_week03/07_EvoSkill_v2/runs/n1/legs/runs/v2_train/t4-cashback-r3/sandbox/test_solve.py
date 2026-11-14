import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", False), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(1000000, "platinum", False), 20000)  # พอดีเพดาน
        self.assertEqual(cashback(10000000, "platinum", True), 20000)

    def test_nodrift(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10067, "silver", False), 151)   # 151.005
        self.assertEqual(cashback(10019, "gold", False), 250)     # 250.475
        self.assertEqual(cashback(10039, "gold", True), 501)      # 501.95
        self.assertEqual(cashback(10001, "silver", True), 150)    # silver ไม่ x2

    def test_reject(self):
        bad = [(4500.0, "gold", False), ("100", "gold", False), (True, "gold", False),
               (None, "gold", False), (-1, "gold", False),
               (10000, "bronze", False), (10000, None, False), (10000, 1, False),
               (10000, "gold", 1), (10000, "gold", None), (10000, "gold", "yes"),
               (50, "bad", False), (-5, "gold", True)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
