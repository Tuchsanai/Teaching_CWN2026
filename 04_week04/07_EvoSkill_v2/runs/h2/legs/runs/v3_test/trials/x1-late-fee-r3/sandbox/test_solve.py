"""ชุดทดสอบ late_fee แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วย Fraction แล้ว (ตรวจซ้ำด้วยสคริปต์ก่อนใส่)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_within_grace_is_free(self):
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(10000, 1), 0)
        self.assertEqual(late_fee(10000, 2), 0)

    def test_after_grace_charges_all_days(self):
        # 10000 * 0.75% * 4 = 300 (นับวันที่ 1–3 ด้วย)
        self.assertEqual(late_fee(10000, 4), 300)
        # 10000 * 0.75% * 10 = 750
        self.assertEqual(late_fee(10000, 10), 750)


class Boundary(unittest.TestCase):
    def test_at_grace_threshold(self):
        self.assertEqual(late_fee(10000, 3), 0)

    def test_just_above_threshold(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_cap_reached_exactly_at_20_days(self):
        # 0.75% * 20 = 15% พอดีเพดาน
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_capped_after_20_days(self):
        self.assertEqual(late_fee(10000, 21), 1500)  # raw 1575 -> เพดาน 1500
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 0), 0)
        self.assertEqual(late_fee(0, 365), 0)


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up(self):
        # 200 * 0.75% * 5 = 7.5 -> ปัดครึ่งขึ้น 8
        self.assertEqual(late_fee(200, 5), 8)

    def test_single_rounding_below_half(self):
        # 50 * 0.75% * 10 = 3.75 -> 4
        self.assertEqual(late_fee(50, 10), 4)
        # 101 * 0.75% * 4 = 3.03 -> 3
        self.assertEqual(late_fee(101, 4), 3)

    def test_cap_rounding(self):
        # เพดาน 101 * 15% = 15.15 -> 15 (ปัดครั้งเดียวหลัง min)
        self.assertEqual(late_fee(101, 21), 15)

    def test_small_amount_rounds_to_zero(self):
        # 10 * 0.75% * 4 = 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)


class Reject(unittest.TestCase):
    def test_amount_bool_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)

    def test_amount_float_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(10000.0, 5)

    def test_amount_str_rejected(self):
        with self.assertRaises(ValueError):
            late_fee("10000", 5)

    def test_amount_negative_rejected(self):
        # ต้องไม่คืน 0 เงียบ ๆ
        with self.assertRaises(ValueError):
            late_fee(-1, 5)

    def test_days_bool_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(10000, True)

    def test_days_float_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 4.0)

    def test_days_str_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(10000, "4")

    def test_days_negative_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(10000, -1)

    def test_days_over_max_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 366)


if __name__ == "__main__":
    unittest.main()
