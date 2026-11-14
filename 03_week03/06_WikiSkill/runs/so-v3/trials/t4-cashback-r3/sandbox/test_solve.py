import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "gold", False), 0)

    def test_min_boundary(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_rates(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_double(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "platinum", True), 8000)

    def test_birthday_silver_no_double(self):
        self.assertEqual(cashback(100000, "silver", True), 1500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)

    def test_floor(self):
        self.assertEqual(cashback(10034, "silver", False), 150)  # 150.51 -> 150

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), (True, "gold", False),
                     (10000, "bronze", False), (10000, "gold", 1), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
