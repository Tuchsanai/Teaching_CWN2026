import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double_gold_platinum(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_birthday_silver_no_double(self):
        self.assertEqual(cashback(10000, "silver", True), 150)

    def test_cap(self):
        self.assertEqual(cashback(10_000_000, "platinum", True), 20000)

    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(10039, "gold", False), 250)

    def test_invalid(self):
        for args in [(1.5, "gold", False), (-1, "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
