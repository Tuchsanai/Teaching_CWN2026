"""ทดสอบ split_bill. expected คำนวณด้วย Fraction ในสคริปต์ก่อนใส่ค่า
รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_no_tip_even(self):
        self.assertEqual(split_bill(9000, 3, 0), [3000, 3000, 3000])

    def test_no_tip_remainder_goes_to_first(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_with_tip(self):
        # 10000 + 10% = 11000 หาร 4 ลงตัว
        self.assertEqual(split_bill(10000, 4, 10), [2750, 2750, 2750, 2750])

    def test_single_person(self):
        # tip = 12345 * 7 / 100 = 864.15 -> ปัดครึ่งขึ้น 864 ; amount = 13209
        self.assertEqual(split_bill(12345, 1, 7), [13209])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_zero_tip(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_max_tip(self):
        self.assertEqual(split_bill(100, 2, 100), [100, 100])

    def test_tip_percent_range_edges(self):
        split_bill(100, 1, 0)  # ต้องไม่ error
        split_bill(100, 1, 100)


class NoDrift(unittest.TestCase):
    def test_tip_rounds_once_half_up(self):
        # tip = 5 * 50 / 100 = 2.5 -> ปัดครึ่งขึ้น = 3 ; amount = 8 ; หาร 1 คน
        self.assertEqual(split_bill(5, 1, 50), [8])

    def test_tip_just_below_half(self):
        # tip = 5 * 49 / 100 = 2.45 -> 2 ; amount = 7
        self.assertEqual(split_bill(5, 1, 49), [7])


class Reject(unittest.TestCase):
    def test_bool_total(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 0)

    def test_float_total(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 2, 0)

    def test_str_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, "2", 0)

    def test_negative_total(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 0)

    def test_zero_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, 0, 0)

    def test_tip_over_100(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, 101)

    def test_negative_tip(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, -1)


if __name__ == "__main__":
    unittest.main()
