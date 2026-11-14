"""ทดสอบ refund() แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วยสคริปต์ Fraction แล้ว (ดู solve.py)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_no_lesson_taken_full_refund(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_half_used_without_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_half_used_with_restock_fee(self):
        # 5000 * 7/8 = 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_zero_used_with_restock_fee(self):
        # 10000 * 7/8 = 8750
        self.assertEqual(refund(10000, 0, True), 8750)


class Boundary(unittest.TestCase):
    def test_exactly_80_percent_still_refunds(self):
        # เกิน 80% เท่านั้นที่ไม่คืน ค่า 80 พอดียังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_exactly_80_percent_with_restock(self):
        # 2000 * 7/8 = 1750
        self.assertEqual(refund(10000, 80, True), 1750)

    def test_just_above_80_percent_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_just_above_80_percent_with_restock_no_refund(self):
        self.assertEqual(refund(10000, 81, True), 0)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)

    def test_100_percent_used_no_refund(self):
        self.assertEqual(refund(10000, 100, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_without_restock(self):
        # 101 * 50/100 = 50.5 -> ปัดลงครั้งเดียว = 50
        # (ถ้าปัดครึ่งขึ้นหรือปัดระหว่างทางจะได้ 51)
        self.assertEqual(refund(101, 50, False), 50)

    def test_single_rounding_with_restock(self):
        # 50.5 * 7/8 = 707/16 = 44.1875 -> 44
        self.assertEqual(refund(101, 50, True), 44)

    def test_fee_applied_once_not_rounded_first(self):
        # 1001 * 7/8 = 7007/8 = 875.875 -> 875
        self.assertEqual(refund(1001, 0, True), 875)

    def test_fractional_chain(self):
        # 99 * 67/100 = 66.33, * 7/8 = 46431/800 = 58.03875 -> 58
        self.assertEqual(refund(99, 33, True), 58)


class Reject(unittest.TestCase):
    def test_paid_float_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000.0, 0, False)

    def test_paid_str_rejected(self):
        with self.assertRaises(ValueError):
            refund("10000", 0, False)

    def test_paid_bool_rejected(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)

    def test_paid_negative_rejected_not_zero(self):
        # ต้อง raise ไม่ใช่คืน 0 เงียบ ๆ
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_used_percent_below_range(self):
        with self.assertRaises(ValueError):
            refund(10000, -1, False)

    def test_used_percent_above_range(self):
        with self.assertRaises(ValueError):
            refund(10000, 101, False)

    def test_used_percent_float_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, 50.0, False)

    def test_used_percent_str_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, "50", False)

    def test_restock_int_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, 50, 1)

    def test_restock_str_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, 50, "yes")

    def test_restock_none_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, 50, None)


if __name__ == "__main__":
    unittest.main()
