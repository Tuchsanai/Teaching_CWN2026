import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_gold(self):
        self.assertEqual(cashback(40000, "gold", False), 1000)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(50000, "platinum", True), 4000)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_cap(self):
        # 500000*4% = 20000 exactly; 500001 still capped; 2x capped
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(1000000, "gold", True), 20000)

    def test_zero(self):
        self.assertEqual(cashback(0, "gold", False), 0)


class NoDrift(unittest.TestCase):
    def test_floor_silver(self):
        # 10001*0.015 = 150.015 -> 150
        self.assertEqual(cashback(10001, "silver", False), 150)

    def test_floor_gold_birthday(self):
        # 10010*0.025*2 = 500.5 -> 500
        self.assertEqual(cashback(10010, "gold", True), 500)

    def test_silver_no_birthday_bonus(self):
        self.assertEqual(cashback(30000, "silver", True), 450)


class Reject(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_str(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_tier(self):
        for t in ("bronze", "GOLD", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)

    def test_birthday(self):
        for b in (1, 0, "yes", None):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)


if __name__ == "__main__":
    unittest.main()
