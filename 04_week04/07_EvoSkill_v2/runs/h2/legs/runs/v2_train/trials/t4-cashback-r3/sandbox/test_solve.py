"""ทดสอบ cashback() แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วย Fraction แล้ว (ดู script ตรวจในบันทึกการทำงาน)
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_each_tier_no_birthday(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_doubles(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, "platinum", True), 0)


class Boundary(unittest.TestCase):
    def test_at_minimum_threshold(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_just_below_threshold(self):
        self.assertEqual(cashback(9999, "silver", False), 0)
        self.assertEqual(cashback(9999, "gold", True), 0)

    def test_cap_exactly_reached(self):
        self.assertEqual(cashback(800000, "gold", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_just_below_cap(self):
        self.assertEqual(cashback(499999, "platinum", False), 19999)

    def test_cap_applies_after_birthday(self):
        self.assertEqual(cashback(1000000, "gold", True), 20000)
        self.assertEqual(cashback(600000, "platinum", False), 20000)


class NoDrift(unittest.TestCase):
    def test_single_rounding_down_at_half(self):
        # 40060 * 2.5% = 1001.5 -> ปัดลงครั้งเดียวได้ 1001
        self.assertEqual(cashback(40060, "gold", False), 1001)

    def test_birthday_before_rounding(self):
        # 1001.5 * 2 = 2003 ต้องไม่ใช่ 2002 (ปัดก่อนคูณ)
        self.assertEqual(cashback(40060, "gold", True), 2003)

    def test_near_cap_not_rounded_up(self):
        # 799999 * 2.5% = 19999.975 -> 19999 ไม่ปัดขึ้นเป็น 20000
        self.assertEqual(cashback(799999, "gold", False), 19999)

    def test_small_fraction_rounds_down(self):
        # 66667 * 1.5% = 1000.005 -> 1000
        self.assertEqual(cashback(66667, "silver", False), 1000)


class Reject(unittest.TestCase):
    def test_bool_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_float_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(4500.0, "gold", False)

    def test_string_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_negative_amount_rejected(self):
        # ค่าติดลบต้อง raise ทั้งที่อยู่ใต้เกณฑ์ 100 บาท (ไม่คืน 0 เงียบ ๆ)
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_unknown_tier_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)

    def test_tier_case_sensitive(self):
        with self.assertRaises(ValueError):
            cashback(10000, "Gold", False)

    def test_non_bool_birthday_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)
        with self.assertRaises(ValueError):
            cashback(10000, "gold", "yes")


if __name__ == "__main__":
    unittest.main()
