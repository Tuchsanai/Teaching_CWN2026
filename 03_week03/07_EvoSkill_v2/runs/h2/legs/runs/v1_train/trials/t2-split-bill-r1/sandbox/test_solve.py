import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_even_split_no_tip(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_with_tip(self):
        # 10000 + 10% = 11000 หารสามได้ 3667, 3667, 3666
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_uneven_total_with_tip(self):
        # 100 หารสามคนไม่ลงตัว คนต้น ๆ จ่ายเพิ่ม 1 สตางค์
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 4, 10), [0, 0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(1, 1, 0), [1])

    def test_tip_zero_and_max(self):
        self.assertEqual(split_bill(10, 1, 0), [10])
        self.assertEqual(split_bill(10, 1, 100), [20])

    def test_fewer_satang_than_people(self):
        self.assertEqual(split_bill(7, 10, 0), [1, 1, 1, 1, 1, 1, 1, 0, 0, 0])


class NoDrift(unittest.TestCase):
    def test_single_rounding_half_up_tie(self):
        # 3 + 50% = 4.5 -> ปัดครึ่งขึ้นครั้งเดียวได้ 5
        self.assertEqual(split_bill(3, 1, 50), [5])

    def test_tie_then_split(self):
        # 1 + 50% = 1.5 -> 2 แล้วหารสามคน
        self.assertEqual(split_bill(1, 3, 50), [1, 1, 0])

    def test_near_half_fraction(self):
        # 999 + 5% = 1048.95 -> 1049
        self.assertEqual(split_bill(999, 1, 5), [1049])

    def test_sum_matches_rounded_amount(self):
        # ผลรวมต้องเท่ายอดที่ปัดแล้วพอดี ไม่มีสตางค์หลุดหรือเกิน
        self.assertEqual(sum(split_bill(1005, 2, 5)), 1055)
        self.assertEqual(split_bill(1005, 2, 5), [528, 527])


class Reject(unittest.TestCase):
    def test_total_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 0)

    def test_total_float_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(1000.0, 2, 0)

    def test_total_str_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill("1000", 2, 0)

    def test_total_negative(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 0)

    def test_people_zero(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 0, 0)

    def test_people_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(1000, True, 0)

    def test_people_float_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 2.0, 0)

    def test_tip_over_100(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 2, 101)

    def test_tip_negative(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 2, -1)

    def test_tip_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 2, True)

    def test_tip_float_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 2, 5.0)

    def test_tip_str_is_not_int(self):
        with self.assertRaises(ValueError):
            split_bill(1000, 2, "10")


if __name__ == "__main__":
    unittest.main()
