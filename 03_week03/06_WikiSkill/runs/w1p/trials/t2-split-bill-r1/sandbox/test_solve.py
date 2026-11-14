import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even_no_tip(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_goes_to_first(self):
        # 1000/3 = 333 เศษ 1
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_with_tip(self):
        # 1000*1.10 = 1100 / 3 = 366 เศษ 2
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_single_person(self):
        self.assertEqual(split_bill(999, 1, 0), [999])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_max_tip(self):
        self.assertEqual(split_bill(500, 2, 100), [500, 500])

    def test_tip_rounding_half_up(self):
        # 5*1.10=5.5 -> ปัดขึ้นเป็น 6 (ข้อสมมติ: ปัดครึ่งขึ้น)
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1*1.01=1.01 -> 1
        self.assertEqual(split_bill(1, 1, 1), [1])

    def test_sum_and_int(self):
        r = split_bill(12345, 7, 15)
        self.assertEqual(sum(r), (12345 * 115 * 2 + 100) // 200)
        for x in r:
            self.assertIs(type(x), int)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_reject_total(self):
        for bad in (-1, 10.0, True, "10", None):
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
