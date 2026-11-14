"""ทดสอบ refund() แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วย Fraction ก่อนใส่ (สูตร: paid*(100-used)/100, ถ้า restock คูณ 7/8, ปัดลงครั้งเดียว, used>80 -> 0)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 20, False), 8000)
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_with_restock_fee(self):
        self.assertEqual(refund(10000, 20, True), 7000)
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_flag_combinations(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)


class Boundary(unittest.TestCase):
    def test_used_exactly_80_still_refundable(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)

    def test_used_81_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_used_100_no_refund(self):
        self.assertEqual(refund(10000, 100, False), 0)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 50, True), 0)

    def test_tiny_amount_rounds_to_zero(self):
        self.assertEqual(refund(1, 1, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_satang_rounds_down(self):
        # 999 * 50/100 = 499.5 -> 499 (ปัดลงครั้งเดียว)
        self.assertEqual(refund(999, 50, False), 499)

    def test_single_rounding_with_fee(self):
        # 1001 * 7/8 = 875.875 -> 875
        self.assertEqual(refund(1001, 0, True), 875)
        # 1000 * 67/100 = 670, * 7/8 = 586.25 -> 586
        self.assertEqual(refund(1000, 33, True), 586)
        # 333 * 90/100 = 299.7, * 7/8 = 262.2375 -> 262
        self.assertEqual(refund(333, 10, True), 262)

    def test_fee_result_half_satang(self):
        # 10000 * 21/100 = 2100, * 7/8 = 1837.5 -> 1837
        self.assertEqual(refund(10000, 79, True), 1837)


class Reject(unittest.TestCase):
    def test_paid_bool_rejected(self):
        with self.assertRaises(ValueError):
            refund(True, 20, False)

    def test_paid_float_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000.0, 20, False)

    def test_paid_str_rejected(self):
        with self.assertRaises(ValueError):
            refund("10000", 20, False)

    def test_paid_negative_rejected(self):
        # ค่าติดลบต้อง raise แม้ used > 80 (ตรวจ input ก่อนเงื่อนไขธุรกิจ)
        with self.assertRaises(ValueError):
            refund(-1, 81, False)

    def test_used_out_of_range(self):
        with self.assertRaises(ValueError):
            refund(10000, -1, False)
        with self.assertRaises(ValueError):
            refund(10000, 101, False)

    def test_used_float_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, 20.0, False)

    def test_used_bool_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, True, False)

    def test_restock_not_bool_rejected(self):
        with self.assertRaises(ValueError):
            refund(10000, 20, 1)
        with self.assertRaises(ValueError):
            refund(10000, 20, "yes")
        with self.assertRaises(ValueError):
            refund(10000, 20, None)


if __name__ == "__main__":
    unittest.main()
