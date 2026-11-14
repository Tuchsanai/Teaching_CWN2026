import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_gold(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_gold_birthday(self):
        self.assertEqual(cashback(10000, "gold", True), 500)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap_exact(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_over(self):
        self.assertEqual(cashback(600000, "platinum", False), 20000)

    def test_birthday_doubled_then_capped(self):
        self.assertEqual(cashback(400000, "gold", True), 20000)

    def test_silver_birthday_no_bonus(self):
        self.assertEqual(cashback(10000, "silver", True), 150)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        self.assertEqual(cashback(10100, "silver", False), 151)  # 151.5

    def test_floor_small(self):
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495

    def test_floor_gold(self):
        self.assertEqual(cashback(10001, "gold", False), 250)  # 250.025

    def test_big_int(self):
        self.assertIsInstance(cashback(10101, "gold", True), int)


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

    def test_bad_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_tier_type(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_birthday_int(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)

    def test_reject_before_early_return(self):
        with self.assertRaises(ValueError):
            cashback(5, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
