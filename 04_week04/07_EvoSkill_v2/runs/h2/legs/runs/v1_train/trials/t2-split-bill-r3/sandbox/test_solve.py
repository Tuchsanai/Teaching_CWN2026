"""ทดสอบ split_bill แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วยสคริปต์ Fraction แล้ว (ดูผลจากการรันสคริปต์ก่อนเขียน test)

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_tip_and_remainder(self):
        # 10000 * 1.10 = 11000 ; 11000 / 3 = 3666 เหลือ 2 -> คนแรก 2 คนจ่ายเพิ่ม
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_no_tip_even_split(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_sum_equals_amount_due(self):
        # 9999 * 1.00 = 9999 ; 9999 / 2 ลงตัว
        self.assertEqual(split_bill(9999, 2, 100), [9999, 9999])
        self.assertEqual(sum(split_bill(12345, 7, 7)), 13209)


class Boundary(unittest.TestCase):
    def test_zero_bill(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])

    def test_one_satang(self):
        self.assertEqual(split_bill(1, 1, 0), [1])
        self.assertEqual(split_bill(1, 4, 25), [1, 0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(6, 7, 0), [1, 1, 1, 1, 1, 1, 0])

    def test_tip_range_ends(self):
        self.assertEqual(split_bill(100, 1, 0), [100])
        self.assertEqual(split_bill(100, 1, 100), [200])


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up(self):
        # 333 * 1.50 = 499.5 -> ปัดครึ่งขึ้นครั้งเดียวได้ 500
        self.assertEqual(split_bill(333, 1, 50), [500])

    def test_no_intermediate_rounding(self):
        # 12345 * 1.07 = 13209.15 -> 13209 (ถ้าปัดทิปก่อนก็ได้ผลเท่ากันในกรณีนี้)
        self.assertEqual(split_bill(12345, 1, 7), [13209])


class Reject(unittest.TestCase):
    def test_bool_total(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)

    def test_float_total(self):
        with self.assertRaises(ValueError):
            split_bill(4500.0, 2, 10)

    def test_str_total(self):
        with self.assertRaises(ValueError):
            split_bill("4500", 2, 10)

    def test_negative_total(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 10)

    def test_people_zero(self):
        with self.assertRaises(ValueError):
            split_bill(4500, 0, 10)

    def test_people_bool(self):
        with self.assertRaises(ValueError):
            split_bill(4500, True, 10)

    def test_tip_over_100(self):
        with self.assertRaises(ValueError):
            split_bill(4500, 2, 101)

    def test_tip_negative(self):
        with self.assertRaises(ValueError):
            split_bill(4500, 2, -1)

    def test_tip_float(self):
        with self.assertRaises(ValueError):
            split_bill(4500, 2, 10.0)


if __name__ == "__main__":
    unittest.main()
