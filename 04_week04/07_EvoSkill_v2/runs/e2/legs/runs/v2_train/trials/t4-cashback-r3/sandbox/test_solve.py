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
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)

    def test_nodrift(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "gold", True), 501)      # 501.65
        self.assertIs(type(cashback(12345, "gold", True)), int)

    def test_reject(self):
        bad = [(-1, "gold", False), (100.0, "gold", False), ("100", "gold", False),
               (True, "gold", False), (None, "gold", False), (10000, "Gold", False),
               (10000, 1, False), (10000, "gold", 1), (10000, "gold", None),
               (-1, "gold", 1), (5, "bad", False)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
