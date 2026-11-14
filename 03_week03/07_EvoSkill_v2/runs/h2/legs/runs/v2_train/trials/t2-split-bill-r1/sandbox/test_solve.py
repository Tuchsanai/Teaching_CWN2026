"""ทดสอบ split_bill แยกหมวด Normal, Boundary, NoDrift, Reject
expected ทุกค่าคำนวณด้วยสคริปต์ Fraction แล้ว (ดู solver-selftest-workflow)
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_basic_no_tip(self):
        # 10000 สตางค์ หาร 3 คน ไม่มีทิป
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_with_tip(self):
        # ทิป 10% ของ 10000 = 1000 รวม 11000 หาร 3 คน
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_with_fractional_tip(self):
        # ทิป 15% ของ 12345 = 1851.75 ปัดครึ่งขึ้นเป็น 1852 รวม 14197 หาร 7 คน
        self.assertEqual(split_bill(12345, 7, 15),
                         [2029, 2028, 2028, 2028, 2028, 2028, 2028])

    def test_even_split(self):
        # หารลงตัวพอดี ทุกคนจ่ายเท่ากัน
        self.assertEqual(split_bill(900, 3, 0), [300, 300, 300])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 4, 50), [0, 0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 0), [999])

    def test_tip_zero_and_hundred(self):
        self.assertEqual(split_bill(999, 1, 0), [999])
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_zero_total_zero_tip_one_person(self):
        self.assertEqual(split_bill(0, 1, 0), [0])

    def test_people_more_than_satang(self):
        # 2 สตางค์หาร 3 คน คนแรก 2 คนได้คนละ 1 ส่วนคนที่สามได้ 0
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])


class NoDrift(unittest.TestCase):
    def test_tip_half_up_then_split(self):
        # ทิป 50% ของ 1 สตางค์ = 0.5 ปัดครึ่งขึ้นเป็น 1 รวม 2 สตางค์
        self.assertEqual(split_bill(1, 2, 50), [1, 1])

    def test_tip_exact_half_is_rounded_once(self):
        # ทิป 50% ของ 3 สตางค์ = 1.5 ปัดเป็น 2 รวม 5 หาร 2 คน
        self.assertEqual(split_bill(3, 2, 50), [3, 2])

    def test_single_rounding_small(self):
        # ทิป 10% ของ 5 สตางค์ = 0.5 ปัดเป็น 1 รวม 6 หาร 2 คน
        self.assertEqual(split_bill(5, 2, 10), [3, 3])

    def test_sum_matches_total_plus_tip(self):
        # ผลรวมต้องเท่ากับยอดบิลบวกทิปที่ปัดแล้วเสมอ
        # 100 สตางค์ ทิป 33% = 33 รวม 133 หาร 3 คน
        self.assertEqual(split_bill(100, 3, 33), [45, 44, 44])
        self.assertEqual(sum(split_bill(100, 3, 33)), 133)


class Reject(unittest.TestCase):
    def test_bool_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)

    def test_float_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000.0, 2, 10)

    def test_string_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill("10000", 2, 10)

    def test_negative_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 10)

    def test_people_zero_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 0, 10)

    def test_people_float_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2.0, 10)

    def test_bool_people_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, True, 10)

    def test_tip_above_100_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, 101)

    def test_tip_negative_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, -1)

    def test_tip_float_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, 10.5)

    def test_tip_string_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, "10")


if __name__ == "__main__":
    unittest.main()
