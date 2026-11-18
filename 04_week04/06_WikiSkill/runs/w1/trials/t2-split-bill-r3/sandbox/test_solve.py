import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even_split_no_tip(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_uneven_first_pay_extra(self):
        # 1000/3 = 333 เศษ 1
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_with_tip(self):
        # 1000*1.10 = 1100 /4 = 275
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_tip_and_remainder(self):
        # 1000*1.15=1150 /3 = 383 เศษ 1
        self.assertEqual(split_bill(1000, 3, 15), [384, 383, 383])

    def test_single_person(self):
        self.assertEqual(split_bill(999, 1, 0), [999])

    def test_edge_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_edge_tip_100(self):
        self.assertEqual(split_bill(101, 2, 100), [101, 101])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_rounding_tip_half_up(self):
        # 5*1.10 = 5.5 -> 6 (ข้อสมมติ: ครึ่งสตางค์ปัดขึ้น)
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1*1.04 = 1.04 -> 1
        self.assertEqual(split_bill(1, 1, 4), [1])

    def test_sum_equals_grand(self):
        r = split_bill(12345, 7, 12)
        self.assertEqual(sum(r), (12345 * 112 + 50) // 100)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_result_is_int(self):
        for x in split_bill(1001, 3, 7):
            self.assertIs(type(x), int)

    def test_reject_total(self):
        for bad in (-1, 10.0, True, "100", None):
            with self.assertRaises(ValueError):
                split_bill(bad, 2, 0)

    def test_reject_people(self):
        for bad in (0, -1, 2.0, True, "2", None):
            with self.assertRaises(ValueError):
                split_bill(100, bad, 0)

    def test_reject_tip_percent(self):
        for bad in (-1, 101, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                split_bill(100, 2, bad)


if __name__ == "__main__":
    unittest.main()
