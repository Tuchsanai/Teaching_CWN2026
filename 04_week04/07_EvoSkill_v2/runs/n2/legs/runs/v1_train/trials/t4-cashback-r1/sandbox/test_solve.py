import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "platinum", True), 1600)
        self.assertEqual(cashback(10020, "gold", True), 501)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_floor_and_silver_birthday(self):
        self.assertEqual(cashback(10015, "platinum", True), 801)
        self.assertEqual(cashback(10000, "silver", True), 300)

    def test_reject(self):
        for a in [(-1, "gold", False), (100.0, "gold", False), ("1", "gold", False),
                  (True, "gold", False), (20000, "bronze", False), (20000, 1, False),
                  (20000, "gold", 1), (9, "x", False)]:
            with self.assertRaises(ValueError):
                cashback(*a)


unittest.main() if __name__ == "__main__" else None
