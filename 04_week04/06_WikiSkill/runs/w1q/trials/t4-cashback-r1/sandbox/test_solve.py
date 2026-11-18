import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal_silver(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_normal_gold(self):
        self.assertEqual(cashback(20000, "gold", False), 500)

    def test_normal_platinum(self):
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday_gold_double(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_birthday_platinum_double(self):
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_birthday_silver_not_doubled(self):
        # policy: silver gets normal rate in birthday month
        self.assertEqual(cashback(20000, "silver", True), 300)

    def test_min_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)

    def test_cap(self):
        # platinum 4% of 500000 = 20000 exactly (cap); above stays capped
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_rounding_floor(self):
        # 10001*0.015 = 150.015 -> 150 ; 10099*0.025=252.475 -> 252
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(10099, "gold", False), 252)
        self.assertEqual(cashback(10039, "silver", False), 150)  # 150.585 -> 150

    def test_result_is_int(self):
        self.assertIs(type(cashback(12345, "gold", True)), int)
        self.assertIs(type(cashback(100, "gold", True)), int)

    def test_reject_amount(self):
        for bad in (-1, 20000.0, True, "20000", None):
            with self.assertRaises(ValueError):
                cashback(bad, "gold", False)

    def test_reject_tier(self):
        for bad in ("bronze", "Gold", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(20000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
