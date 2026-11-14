import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_normal_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_normal_uneven_first_pay_more(self):
        # 10000 + 10% = 11000 -> 3667, 3667, 3666
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_normal_single_person(self):
        self.assertEqual(split_bill(1000, 1, 0), [1000])

    def test_edge_zero_total(self):
        self.assertEqual(split_bill(0, 2, 50), [0, 0])

    def test_edge_tip_max(self):
        self.assertEqual(split_bill(500, 2, 100), [500, 500])

    def test_edge_more_people_than_satang(self):
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_rounding_tip_half_up(self):
        # 1005*1.10 = 1105.5 -> 1106 (ข้อสมมติ: ปัดครึ่งขึ้น) -> 553, 553
        self.assertEqual(split_bill(1005, 2, 10), [553, 553])

    def test_rounding_remainder(self):
        # 999*1.01 = 1008.99 -> 1009 -> 253, 252, 252, 252
        self.assertEqual(split_bill(999, 4, 1), [253, 252, 252, 252])

    def test_result_is_int(self):
        for x in split_bill(1005, 3, 7):
            self.assertIs(type(x), int)

    def test_reject_total(self):
        for v in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                split_bill(v, 2, 10)

    def test_reject_people(self):
        for v in (0, -1, 2.0, True, "2", None):
            with self.assertRaises(ValueError):
                split_bill(100, v, 10)

    def test_reject_tip_percent(self):
        for v in (-1, 101, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                split_bill(100, 2, v)


if __name__ == "__main__":
    unittest.main()
