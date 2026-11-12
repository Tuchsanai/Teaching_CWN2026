import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_rates_at_minimum(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_half_up_single_rounding(self):
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10100, "silver", False), 152)   # 151.5 -> 152

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), (True, "gold", False),
                     ("100", "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
