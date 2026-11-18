import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even_no_tip(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_uneven_remainder_goes_to_first(self):
        # 1000/3 = 333 เศษ 1 -> คนแรกจ่ายเพิ่ม 1
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_with_tip(self):
        # 1000 + 10% = 1100 / 2
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_multiple_extra(self):
        # 10 / 4 = 2 เศษ 2 -> สองคนแรกจ่าย 3
        self.assertEqual(split_bill(10, 4, 0), [3, 3, 2, 2])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_single_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_tip_rounding_half_up(self):
        # 105*1.05 = 110.25 -> 110 ; 110*1.05... ใช้ 10*5% = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(1, 1, 49), [1])  # 1.49 -> 1
        self.assertEqual(split_bill(1, 1, 50), [2])  # 1.50 -> 2 (ปัดครึ่งขึ้น)

    def test_sum_and_int(self):
        r = split_bill(12345, 7, 15)
        self.assertEqual(sum(r), (12345 * 115 * 2 + 100) // 200)
        for x in r:
            self.assertIs(type(x), int)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_reject_total(self):
        for bad in (-1, 10.0, True, "100", None):
            with self.assertRaises(ValueError):
                split_bill(bad, 2, 10)

    def test_reject_people(self):
        for bad in (0, -1, 2.0, True, "2", None):
            with self.assertRaises(ValueError):
                split_bill(100, bad, 10)

    def test_reject_tip_percent(self):
        for bad in (-1, 101, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                split_bill(100, 2, bad)


if __name__ == "__main__":
    unittest.main()
