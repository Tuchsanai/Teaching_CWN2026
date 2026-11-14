"""ทดสอบ late_fee. รัน: python3 -m unittest -v test_solve
expected ทุกค่าคำนวณด้วยสคริปต์ Fraction แล้ว (ดูคอมเมนต์ในแต่ละกรณี)
"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic_over_grace(self):
        self.assertEqual(late_fee(10000, 4), 300)    # 10000 * 0.75% * 4 = 300
        self.assertEqual(late_fee(10000, 5), 375)    # 10000 * 0.75% * 5 = 375
        self.assertEqual(late_fee(7000, 10), 525)    # 7000 * 0.75% * 10 = 525

    def test_small_amount(self):
        self.assertEqual(late_fee(200, 4), 6)        # 200 * 3% = 6

    def test_all_days_counted_including_first_three(self):
        # 10 วันที่ช้า คิด 10 วันเต็ม ไม่ใช่ 7 วัน (ต้องรวม 3 วันแรก)
        self.assertEqual(late_fee(10000, 10), 750)   # 10000 * 0.75% * 10 = 750


class Boundary(unittest.TestCase):
    def test_at_grace_threshold_is_free(self):
        self.assertEqual(late_fee(10000, 3), 0)      # ช้า 3 วันพอดี ไม่คิด

    def test_just_above_grace(self):
        self.assertEqual(late_fee(10000, 4), 300)    # 4 วัน เริ่มคิด

    def test_zero_days_and_zero_amount(self):
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(0, 365), 0)        # ยอด 0 ได้ 0 เสมอ

    def test_cap_reached_exactly_at_20_days(self):
        # 0.75% * 20 = 15% พอดี -> 10000 * 15% = 1500
        self.assertEqual(late_fee(10000, 19), 1425)  # ก่อนถึงเพดาน
        self.assertEqual(late_fee(10000, 20), 1500)  # ถึงเพดานพอดี

    def test_cap_holds_beyond_20_days(self):
        self.assertEqual(late_fee(10000, 21), 1500)  # 1575 ถูกตัดเหลือ 1500
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_max_days_small_amount(self):
        self.assertEqual(late_fee(1, 365), 0)        # เพดาน 0.15 ปัดครึ่งขึ้นได้ 0


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up(self):
        self.assertEqual(late_fee(50, 4), 2)         # 1.5 -> 2 (ปัดครึ่งขึ้น)
        self.assertEqual(late_fee(250, 4), 8)        # 7.5 -> 8

    def test_no_early_rounding_before_cap(self):
        # 333 * 15% = 49.95 -> 50 (ถ้าปัดลงก่อนเทียบเพดานจะได้ 49)
        self.assertEqual(late_fee(333, 20), 50)
        # 333 * 0.75% * 19 = 47.4525 -> 47
        self.assertEqual(late_fee(333, 19), 47)

    def test_fraction_below_half_rounds_down(self):
        self.assertEqual(late_fee(10001, 4), 300)    # 300.03 -> 300


class Reject(unittest.TestCase):
    def test_amount_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(True, 4)

    def test_amount_float_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000.0, 4)

    def test_amount_string_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee("10000", 4)

    def test_amount_negative(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 4)

    def test_amount_negative_below_grace_still_raises(self):
        # ต้องตรวจ input ก่อนเงื่อนไข "ไม่เกิน 3 วันไม่คิดค่าปรับ"
        with self.assertRaises(ValueError):
            late_fee(-1, 2)

    def test_days_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000, True)

    def test_days_float_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 4.0)

    def test_days_string_is_not_int(self):
        with self.assertRaises(ValueError):
            late_fee(10000, "4")

    def test_days_negative(self):
        with self.assertRaises(ValueError):
            late_fee(10000, -1)

    def test_days_above_max(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 366)


if __name__ == "__main__":
    unittest.main()
