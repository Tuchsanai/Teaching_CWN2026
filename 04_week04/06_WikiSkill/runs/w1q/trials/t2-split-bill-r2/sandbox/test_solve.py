import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even_no_tip(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_uneven_remainder_goes_to_first(self):
        # 1000/3 = 333 เศษ 1
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_with_tip(self):
        # 1000 + 10% = 1100 / 4 = 275
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_tip_and_remainder(self):
        # 1000 + 15% = 1150 / 3 = 383 เศษ 1
        self.assertEqual(split_bill(1000, 3, 15), [384, 383, 383])

    def test_single_person(self):
        self.assertEqual(split_bill(999, 1, 0), [999])

    def test_total_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_remainder_max(self):
        # 10/3... total=5, 3 คน -> 1 เศษ 2
        self.assertEqual(split_bill(5, 3, 0), [2, 2, 1])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_tip_max_boundary(self):
        self.assertEqual(split_bill(1000, 2, 100), [1000, 1000])

    def test_tip_fraction_rounds_half_up(self):
        # ข้อสมมติ: 5 + 10% = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 4 + 10% = 4.4 -> 4
        self.assertEqual(split_bill(4, 1, 10), [4])

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
