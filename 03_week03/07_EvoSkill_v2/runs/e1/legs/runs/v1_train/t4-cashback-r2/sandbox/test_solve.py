import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_values(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "silver", True), 150)
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10001, "silver", False), 150)  # floor 150.015
        self.assertEqual(cashback(10033, "gold", False), 250)    # 250.825 -> 250
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", True), 20000)
        self.assertEqual(cashback(250000, "gold", True), 12500)
        self.assertEqual(cashback(10**7, "silver", False), 20000)
        self.assertEqual(type(cashback(12345, "gold", True)), int)

    def test_reject(self):
        for a in [(-1, "gold", False), (1.0, "gold", False), ("1", "gold", False),
                  (True, "gold", False), (None, "gold", False), (100, "bronze", False),
                  (100, None, False), (100, "gold", 1), (100, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
