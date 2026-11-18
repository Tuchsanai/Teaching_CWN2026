"""ชุดทดสอบ split_bill. expected คำนวณด้วยสคริปต์ Fraction แล้ว

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_basic_with_tip_and_remainder(self):
        # 10000 + ทิป 10% (1000) = 11000 หาร 3 -> 3667, 3667, 3666
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_no_tip_even_split(self):
        self.assertEqual(split_bill(9000, 3, 0), [3000, 3000, 3000])

    def test_one_person(self):
        self.assertEqual(split_bill(5000, 1, 0), [5000])

    def test_larger_group_with_remainder(self):
        # 12345 + ทิป 8% (988) = 13333 หาร 7 -> เศษ 5 คนแรกได้ +1
        self.assertEqual(split_bill(12345, 7, 8),
                         [1905, 1905, 1905, 1905, 1905, 1904, 1904])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 4, 0), [0, 0, 0, 0])

    def test_zero_total_with_max_tip(self):
        self.assertEqual(split_bill(0, 1, 100), [0])

    def test_minimum_people_and_tip_zero(self):
        self.assertEqual(split_bill(1, 1, 0), [1])

    def test_tip_max_100_doubles_total(self):
        # ทิป 100% -> ยอดรวม = 2 * 250 = 500 หาร 2
        self.assertEqual(split_bill(250, 2, 100), [250, 250])

    def test_tiny_total_tip_half_up_then_split(self):
        # ทิป 50% ของ 1 = 0.5 -> 1 -> รวม 2 หาร 2 -> 1, 1
        self.assertEqual(split_bill(1, 2, 50), [1, 1])
        # 0 หาร 3 คน -> ทุกคนจ่าย 0
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_tip_half_rounds_up_once(self):
        # ทิป 50% ของ 101 = 50.5 -> ปัดครึ่งขึ้น 51 -> รวม 152 (ไม่ใช่ 151)
        self.assertEqual(split_bill(101, 1, 50), [152])

    def test_tip_half_rounds_up_then_split(self):
        # ทิป 5% ของ 250 = 12.5 -> 13 -> รวม 263 หาร 2 -> 132, 131
        self.assertEqual(split_bill(250, 2, 5), [132, 131])

    def test_sum_always_equals_total_plus_rounded_tip(self):
        for total, people, tip in [(9999, 2, 15), (100, 3, 33), (12345, 7, 8)]:
            with self.subTest(total=total, people=people, tip=tip):
                tip_amt = (total * tip * 2 + 100) // 200  # half-up แบบจำนวนเต็ม
                self.assertEqual(sum(split_bill(total, people, tip)), total + tip_amt)


class Reject(unittest.TestCase):
    def test_bool_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)

    def test_float_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000.0, 2, 10)

    def test_str_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill("10000", 2, 10)

    def test_negative_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 10)

    def test_zero_people_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 0, 10)

    def test_float_people_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2.0, 10)

    def test_tip_above_100_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, 101)

    def test_negative_tip_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, -1)

    def test_bool_tip_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(10000, 2, False)


if __name__ == "__main__":
    unittest.main()
