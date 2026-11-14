import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_min_boundary(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_rates(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_double(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_birthday_silver_no_double(self):
        self.assertEqual(cashback(100000, "silver", True), 1500)

    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_invalid(self):
        for a in [(1.5, "gold", False), (-1, "gold", False),
                  (True, "gold", False), (100, "x", False),
                  (100, "gold", 1)]:
            with self.assertRaises(ValueError):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
