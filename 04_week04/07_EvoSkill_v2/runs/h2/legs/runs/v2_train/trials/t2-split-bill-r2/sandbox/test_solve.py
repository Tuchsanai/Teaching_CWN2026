"""ทดสอบ split_bill แยกหมวด Normal, Boundary, NoDrift, Reject
expected คำนวณด้วยสคริปต์ Fraction แยกต่างหากแล้ว

รัน: python3 -m unittest -v test_solve
"""
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_basic_with_remainder(self):
        # 10000 + 10% = 11000 หาร 3 -> เศษ 2 สตางค์ให้คนแรก 2 คน
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_tip_rounds_half_up_then_splits(self):
        # 12345 * 15% = 1851.75 -> ปัด 1852 -> ยอด 14197 หาร 4
        self.assertEqual(split_bill(12345, 4, 15), [3550, 3549, 3549, 3549])

    def test_seven_people_many_remainder(self):
        # 12345 * 8% = 987.6 -> 988 -> ยอด 13333 หาร 7
        self.assertEqual(split_bill(12345, 7, 8),
                         [1905, 1905, 1905, 1905, 1905, 1904, 1904])

    def test_no_tip(self):
        self.assertEqual(split_bill(5000, 4, 0), [1250, 1250, 1250, 1250])

    def test_result_sums_to_due_amount(self):
        result = split_bill(12345, 7, 8)
        self.assertEqual(sum(result), 13333)
        self.assertEqual(len(result), 7)


class Boundary(unittest.TestCase):
    def test_single_person(self):
        self.assertEqual(split_bill(100, 1, 0), [100])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_one_satang_among_three(self):
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_tip_zero_and_max(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])
        # 1000 + 100% = 2000 หาร 2
        self.assertEqual(split_bill(1000, 2, 100), [1000, 1000])

    def test_tip_max_with_remainder(self):
        # 1000 + 33% = 1330 หาร 3
        self.assertEqual(split_bill(1000, 3, 33), [444, 443, 443])


class NoDrift(unittest.TestCase):
    def test_single_rounding_at_tip_half(self):
        # 10 * 5% = 0.5 -> ปัดครึ่งขึ้น 1 -> ยอด 11 หาร 2
        self.assertEqual(split_bill(10, 2, 5), [6, 5])

    def test_half_satang_tip_not_double_rounded(self):
        # 999 * 5% = 49.95 -> 50 -> ยอด 1049 หาร 2
        self.assertEqual(split_bill(999, 2, 5), [525, 524])


class Reject(unittest.TestCase):
    def test_total_bool_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 0)

    def test_total_float_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 2, 0)

    def test_total_str_rejected(self):
        with self.assertRaises(ValueError):
            split_bill("100", 2, 0)

    def test_total_negative_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 0)

    def test_people_zero_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 0, 0)

    def test_people_bool_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, True, 0)

    def test_people_float_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2.0, 0)

    def test_tip_above_100_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, 101)

    def test_tip_negative_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, -1)

    def test_tip_float_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, 10.0)

    def test_tip_str_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, "10")


if __name__ == "__main__":
    unittest.main()
