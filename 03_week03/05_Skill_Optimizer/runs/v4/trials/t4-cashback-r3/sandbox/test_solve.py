import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "silver", False), 0)

    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up_rounding(self):
        # 10010*15/1000 = 150.15 -> 150 ; 10033*15/1000=150.495 -> 150
        self.assertEqual(cashback(10033, "silver", False), 150)
        # 10010*25/1000 = 250.25 ; 10030*25/1000 = 250.75 -> 251
        self.assertEqual(cashback(10030, "gold", False), 251)
        # 10010*15/1000... exact .5: 10100*15/1000=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_invalid_inputs(self):
        for args in [(-1, "gold", False), (100.0, "gold", False),
                     (True, "gold", False), ("100", "gold", False),
                     (10000, "bronze", False), (10000, 1, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
