import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_gold(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_gold_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_cap_exact(self):
        self.assertEqual(cashback(800000, "gold", False), 20000)

    def test_below_cap(self):
        self.assertEqual(cashback(799999, "gold", False), 19999)

    def test_cap_after_double(self):
        self.assertEqual(cashback(600000, "platinum", True), 20000)

    def test_silver_birthday_no_double(self):
        self.assertEqual(cashback(10000, "silver", True), 150)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)


class NoDrift(unittest.TestCase):
    def test_floor_half(self):
        self.assertEqual(cashback(10100, "silver", False), 151)  # 151.5

    def test_floor_fraction(self):
        self.assertEqual(cashback(10001, "gold", False), 250)  # 250.025

    def test_floor_birthday(self):
        self.assertEqual(cashback(10101, "gold", True), 505)  # 505.05


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_negative(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_tier_type(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_birthday(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)

    def test_reject_before_early_return(self):
        with self.assertRaises(ValueError):
            cashback(50, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
