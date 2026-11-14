import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_gold(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(10000, "platinum", True), 800)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)

    def test_just_under_cap(self):
        self.assertEqual(cashback(499999, "platinum", False), 19999)

    def test_silver_birthday_no_bonus(self):
        self.assertEqual(cashback(10000, "silver", True), 150)


class NoDrift(unittest.TestCase):
    def test_floor_silver(self):
        self.assertEqual(cashback(10066, "silver", False), 150)  # 150.99

    def test_floor_gold(self):
        self.assertEqual(cashback(10039, "gold", False), 250)  # 250.975

    def test_floor_gold_birthday(self):
        self.assertEqual(cashback(10019, "gold", True), 500)  # 500.95


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_negative(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_birthday(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)

    def test_validate_before_shortcut(self):
        with self.assertRaises(ValueError):
            cashback(50, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
