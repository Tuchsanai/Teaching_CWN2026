import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even_no_tip(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_goes_to_first(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_with_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_single_person(self):
        self.assertEqual(split_bill(999, 1, 10), [1099])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_max_tip(self):
        self.assertEqual(split_bill(100, 3, 100), [67, 67, 66])

    def test_tip_rounding_half_up(self):
        # 105*10% = 10.5 -> ปัดขึ้นเป็น 11 (ข้อสมมติ) -> 116
        self.assertEqual(split_bill(105, 1, 10), [116])

    def test_sum_and_fair(self):
        r = split_bill(12345, 7, 15)
        self.assertEqual(sum(r), 12345 + (12345 * 15 * 2 + 100) // 200)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_result_int(self):
        for x in split_bill(1001, 3, 7):
            self.assertIs(type(x), int)

    def test_reject_total(self):
        for v in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                split_bill(v, 2, 10)

    def test_reject_people(self):
        for v in (0, -1, 2.0, True, "2"):
            with self.assertRaises(ValueError):
                split_bill(100, v, 10)

    def test_reject_tip(self):
        for v in (-1, 101, 10.0, True, "10"):
            with self.assertRaises(ValueError):
                split_bill(100, 2, v)


if __name__ == "__main__":
    unittest.main()
