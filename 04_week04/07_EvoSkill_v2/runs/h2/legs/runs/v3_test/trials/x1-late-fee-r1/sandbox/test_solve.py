"""ชุดทดสอบ late_fee แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วยสคริปต์ Fraction แล้ว (ดูผลในคำตอบ)
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(10000, 4), 300)      # 10000 * 4 * 0.75%
        self.assertEqual(late_fee(10000, 10), 750)
        self.assertEqual(late_fee(100000, 7), 5250)

    def test_fee_is_under_cap(self):
        self.assertEqual(late_fee(10000, 15), 1125)    # 11.25% < 15%


class Boundary(unittest.TestCase):
    def test_at_grace_threshold(self):
        self.assertEqual(late_fee(10000, 3), 0)        # พอดี 3 วัน ไม่คิด
        self.assertEqual(late_fee(10000, 4), 300)      # 4 วันเริ่มคิด

    def test_zero_days(self):
        self.assertEqual(late_fee(10000, 0), 0)

    def test_cap_reached_at_20_days(self):
        self.assertEqual(late_fee(1000, 19), 143)      # 142.5 -> ปัดขึ้น 143
        self.assertEqual(late_fee(1000, 20), 150)      # พอดีเพดาน 15%
        self.assertEqual(late_fee(1000, 21), 150)      # 157.5 ถูกตัดที่เพดาน

    def test_max_days(self):
        self.assertEqual(late_fee(10000, 365), 1500)   # เพดาน 15%
        self.assertEqual(late_fee(1000, 365), 150)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 365), 0)
        self.assertEqual(late_fee(0, 4), 0)


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up(self):
        # 50 * 4 * 0.75% = 1.5 -> ปัดครั้งเดียวได้ 2 (ปัดลงก่อนคูณจะได้ 1)
        self.assertEqual(late_fee(50, 4), 2)
        # 250 * 4 * 0.75% = 7.5 -> 8
        self.assertEqual(late_fee(250, 4), 8)
        # 200 * 4 * 0.75% = 6.0 (ไม่มีทศนิยม)
        self.assertEqual(late_fee(200, 4), 6)

    def test_cap_applied_before_rounding(self):
        # ค่าปรับดิบ 27.375 แต่เพดาน 15% = 1.5 -> ปัดครั้งเดียวได้ 2
        self.assertEqual(late_fee(10, 365), 2)
        # ค่าปรับดิบ 2.7375, เพดาน 0.15 -> 0
        self.assertEqual(late_fee(1, 365), 0)


class Reject(unittest.TestCase):
    def test_amount_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)

    def test_amount_float_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000.0, 5)

    def test_amount_str_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee("10000", 5)

    def test_amount_negative(self):
        # ค่าติดลบต้อง raise ไม่ใช่คืน 0 เงียบ ๆ แม้จะอยู่ในช่วงผ่อนผัน
        with self.assertRaises(ValueError):
            late_fee(-1, 2)
        with self.assertRaises(ValueError):
            late_fee(-1, 10)

    def test_days_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000, True)

    def test_days_float_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 4.0)

    def test_days_str_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000, "4")

    def test_days_negative(self):
        with self.assertRaises(ValueError):
            late_fee(10000, -1)

    def test_days_over_365(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 366)


if __name__ == "__main__":
    unittest.main()
