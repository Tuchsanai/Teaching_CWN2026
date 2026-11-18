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

    def test_birthday_silver_not_double(self):
        # นโยบายร้าน: silver ไม่ได้ 2 เท่า
        self.assertEqual(cashback(20000, "silver", True), 300)

    def test_min_amount_boundary(self):
        self.assertEqual(cashback(9999, "platinum", False), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)

    def test_cap_boundary(self):
        # platinum 500000*4% = 20000 พอดี
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)

    def test_cap_with_birthday(self):
        self.assertEqual(cashback(1000000, "gold", True), 20000)

    def test_rounding_floor(self):
        # 10033*1.5% = 150.495 -> 150 ; 10100*1.5%=151.5 -> 151 (ปัดลง)
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10100, "silver", False), 151)

    def test_returns_int(self):
        self.assertIs(type(cashback(12345, "gold", True)), int)
        self.assertIs(type(cashback(0, "gold", False)), int)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, "silver", False), 0)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
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
