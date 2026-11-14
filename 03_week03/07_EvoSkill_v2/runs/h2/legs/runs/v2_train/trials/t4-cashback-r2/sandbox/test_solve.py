"""test ของ cashback() แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วยสคริปต์ Fraction แล้ว

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_no_birthday_each_tier(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_doubles_each_tier(self):
        self.assertEqual(cashback(10000, "silver", True), 300)
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_uncapped_large_amount(self):
        self.assertEqual(cashback(1000000, "silver", False), 15000)


class Boundary(unittest.TestCase):
    def test_exactly_100_baht_is_eligible(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_just_below_100_baht_gets_nothing(self):
        self.assertEqual(cashback(9999, "gold", False), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_cap_reached_exactly(self):
        # 400000 * 2.5% * 2 = 20000 พอดีเพดาน
        self.assertEqual(cashback(400000, "gold", True), 20000)

    def test_just_below_cap(self):
        # 399999 * 5% = 19999.95 -> 19999
        self.assertEqual(cashback(399999, "gold", True), 19999)

    def test_cap_applies_to_large_amounts(self):
        self.assertEqual(cashback(1000000, "gold", False), 20000)
        self.assertEqual(cashback(1000000, "silver", True), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)


class NoDrift(unittest.TestCase):
    def test_single_rounding_at_end(self):
        # 10001 * 8% = 800.08 -> 800 (ไม่ปัดระหว่างทาง)
        self.assertEqual(cashback(10001, "platinum", True), 800)

    def test_half_rounds_down_for_payout(self):
        # 10100 * 1.5% = 151.5 -> 151 (ร้านจ่ายออก ปัดลง)
        self.assertEqual(cashback(10100, "silver", False), 151)

    def test_birthday_doubles_before_floor(self):
        # 13333 * 1.5% = 199.995 -> ปัดหลังคูณ 2 = 399.99 -> 399
        self.assertEqual(cashback(13333, "silver", True), 399)

    def test_gold_small_fraction(self):
        # 10001 * 2.5% = 250.025 -> 250
        self.assertEqual(cashback(10001, "gold", False), 250)


class Reject(unittest.TestCase):
    def test_bool_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_float_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_string_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_negative_amount_rejected_not_zero(self):
        # ค่าติดลบอยู่ใต้ขั้นต่ำ 100 บาท ต้อง raise ไม่ใช่คืน 0
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_unknown_tier_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_tier_case_must_match(self):
        with self.assertRaises(ValueError):
            cashback(10000, "Gold", False)

    def test_tier_none_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_birthday_must_be_bool(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)
        with self.assertRaises(ValueError):
            cashback(10000, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
