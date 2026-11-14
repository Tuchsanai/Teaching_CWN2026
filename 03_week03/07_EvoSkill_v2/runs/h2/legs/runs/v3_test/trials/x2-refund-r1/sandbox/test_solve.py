"""ทดสอบ refund() ของ solve.py
รัน: python3 -m unittest -v test_solve
expected ทุกค่าคำนวณด้วยสคริปต์ Fraction ก่อนใส่
"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 30, False), 7000)

    def test_restock_deducts_12_5_percent(self):
        self.assertEqual(refund(10000, 30, True), 6125)

    def test_no_progress_full_refund(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_flag_combinations(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)


class Boundary(unittest.TestCase):
    def test_exactly_80_percent_still_refundable(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_just_above_80_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_zero_and_max(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_single_rounding_round_down(self):
        # 100 * 7/8 = 87.5 -> ปัดลงได้ 87 (ปัดครึ่งขึ้นจะได้ 88)
        self.assertEqual(refund(100, 0, True), 87)

    def test_single_rounding_large(self):
        # 10001 * 7/8 = 8750.875 -> 8750
        self.assertEqual(refund(10001, 0, True), 8750)

    def test_fraction_remaining_then_fee(self):
        # 1000 * 55/100 * 7/8 = 481.25 -> 481
        self.assertEqual(refund(1000, 45, True), 481)
        # 99 * 67/100 * 7/8 = 58.03875 -> 58
        self.assertEqual(refund(99, 33, True), 58)


class Reject(unittest.TestCase):
    def test_bool_paid_rejected(self):
        with self.assertRaises(ValueError):
            refund(True, 30, False)

    def test_float_paid_rejected(self):
        with self.assertRaises(ValueError):
            refund(4500.0, 30, False)

    def test_string_paid_rejected(self):
        with self.assertRaises(ValueError):
            refund("4500", 30, False)

    def test_negative_paid_rejected(self):
        with self.assertRaises(ValueError):
            refund(-1, 30, False)

    def test_used_percent_out_of_range(self):
        with self.assertRaises(ValueError):
            refund(10000, -1, False)
        with self.assertRaises(ValueError):
            refund(10000, 101, False)

    def test_used_percent_wrong_type(self):
        with self.assertRaises(ValueError):
            refund(10000, 30.0, False)
        with self.assertRaises(ValueError):
            refund(10000, True, False)

    def test_restock_must_be_bool(self):
        with self.assertRaises(ValueError):
            refund(10000, 30, 1)
        with self.assertRaises(ValueError):
            refund(10000, 30, "yes")

    def test_invalid_input_above_cutoff_still_raises(self):
        # ค่าผิดต้อง raise ก่อนเงื่อนไข 80% ไม่คืน 0 เงียบ ๆ
        with self.assertRaises(ValueError):
            refund(-1, 90, False)
        with self.assertRaises(ValueError):
            refund(10000, 101, False)


if __name__ == "__main__":
    unittest.main()
