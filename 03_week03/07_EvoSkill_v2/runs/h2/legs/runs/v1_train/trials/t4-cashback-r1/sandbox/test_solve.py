"""ชุดทดสอบ cashback: หมวด Normal, Boundary, NoDrift, Reject

รัน: python3 -m unittest -v test_solve
expected คำนวณด้วย Fraction แล้วจึงใส่ไว้ (ดูหมายเหตุในแต่ละ test)
"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_basic_tiers(self):
        # 10000 * 3/200 = 150 ; 10000 * 1/40 = 250 ; 10000 * 1/25 = 400
        self.assertEqual(cashback(10_000, "silver", False), 150)
        self.assertEqual(cashback(10_000, "gold", False), 250)
        self.assertEqual(cashback(10_000, "platinum", False), 400)

    def test_birthday_doubles(self):
        # 250*2 = 500 ; 400*2 = 800
        self.assertEqual(cashback(10_000, "gold", True), 500)
        self.assertEqual(cashback(10_000, "platinum", True), 800)


class Boundary(unittest.TestCase):
    def test_at_threshold_qualifies(self):
        # ยอด 100 บาทพอดี ได้เงินคืน: 10000 * 3/200 = 150
        self.assertEqual(cashback(10_000, "silver", False), 150)

    def test_just_below_threshold_gets_zero(self):
        self.assertEqual(cashback(9_999, "platinum", True), 0)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, "platinum", True), 0)

    def test_cap_reached_exactly(self):
        # platinum 500000 * 4% = 20000 พอดีเพดาน
        self.assertEqual(cashback(500_000, "platinum", False), 20_000)

    def test_cap_applies_above(self):
        # 1000000 * 4% = 40000 -> เพดาน 20000
        self.assertEqual(cashback(1_000_000, "platinum", False), 20_000)
        # gold เดือนเกิด 1000000 * 2.5% * 2 = 50000 -> เพดาน 20000
        self.assertEqual(cashback(1_000_000, "gold", True), 20_000)


class NoDrift(unittest.TestCase):
    def test_single_rounding_after_birthday(self):
        # 10020 * 1/40 = 250.5 ; *2 = 501 (ถ้าปัดก่อนคูณจะได้ 500)
        self.assertEqual(cashback(10_020, "gold", True), 501)

    def test_rounds_down_at_half(self):
        # 10100 * 3/200 = 151.5 -> ปัดลง 151
        self.assertEqual(cashback(10_100, "silver", False), 151)


class Reject(unittest.TestCase):
    def test_bool_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_float_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10_000.0, "gold", False)

    def test_string_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_unknown_tier_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10_000, "bronze", False)

    def test_tier_case_must_match(self):
        with self.assertRaises(ValueError):
            cashback(10_000, "Gold", False)

    def test_birthday_must_be_bool(self):
        with self.assertRaises(ValueError):
            cashback(10_000, "gold", 1)
        with self.assertRaises(ValueError):
            cashback(10_000, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
