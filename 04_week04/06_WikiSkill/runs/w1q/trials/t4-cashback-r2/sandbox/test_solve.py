import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal_silver(self):
        self.assertEqual(cashback(50000, "silver", False), 750)

    def test_normal_gold(self):
        self.assertEqual(cashback(50000, "gold", False), 1250)

    def test_normal_platinum(self):
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_birthday_gold_double(self):
        self.assertEqual(cashback(50000, "gold", True), 2500)

    def test_birthday_platinum_double(self):
        self.assertEqual(cashback(50000, "platinum", True), 4000)

    def test_birthday_silver_no_double(self):
        # นโยบายร้าน: silver ไม่ได้ 2 เท่า
        self.assertEqual(cashback(50000, "silver", True), 750)

    def test_min_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        # platinum 4% ของ 500000 = 20000 พอดีเพดาน
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)
        self.assertEqual(cashback(10**7, "gold", True), 20000)

    def test_cap_after_double(self):
        # gold 2.5% x2 = 5% ของ 400000 = 20000; 500000 -> 25000 ถูกจำกัด
        self.assertEqual(cashback(400000, "gold", True), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)

    def test_rounding_floor(self):
        # 10001*1.5% = 150.015 -> 150 ; 10033*1.5% = 150.495 -> 150
        self.assertEqual(cashback(10033, "silver", False), 150)
        # 10039*2.5% = 250.975 -> 250 (ปัดลง)
        self.assertEqual(cashback(10039, "gold", False), 250)
        # 10013*5% = 500.65 -> 500
        self.assertEqual(cashback(10013, "gold", True), 500)

    def test_result_int(self):
        self.assertIs(type(cashback(12345, "gold", True)), int)
        self.assertIs(type(cashback(100, "gold", True)), int)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                cashback(bad, "gold", False)

    def test_reject_tier(self):
        for bad in ("bronze", "Gold", "", None, 1, True):
            with self.assertRaises(ValueError):
                cashback(20000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cashback(20000, "gold", bad)


if __name__ == "__main__":
    unittest.main()
