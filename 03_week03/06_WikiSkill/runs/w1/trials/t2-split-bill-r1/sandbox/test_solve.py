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
        self.assertEqual(split_bill(999, 1, 0), [999])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_max_tip(self):
        self.assertEqual(split_bill(1000, 3, 100), [667, 667, 666])

    def test_tip_rounding_half_up(self):
        # 101 * 1.05 = 106.05 -> 106 ; 5 สตางค์ทิปปัดลง
        self.assertEqual(split_bill(101, 1, 5), [106])
        # 110 * 1.05 = 115.5 -> 116 (ข้อสมมติ: ปัดครึ่งขึ้น)
        self.assertEqual(split_bill(110, 1, 5), [116])

    def test_sum_and_type(self):
        r = split_bill(12345, 7, 13)
        self.assertEqual(sum(r), (12345 * 113 * 2 + 100) // 200)
        self.assertEqual(len(r), 7)
        for x in r:
            self.assertIs(type(x), int)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_reject_total(self):
        for bad in (-1, 10.0, True, "5", None):
            with self.assertRaises(ValueError):
                split_bill(bad, 2, 0)

    def test_reject_people(self):
        for bad in (0, -2, 2.0, True, "2", None):
            with self.assertRaises(ValueError):
                split_bill(100, bad, 0)

    def test_reject_tip(self):
        for bad in (-1, 101, 10.5, False, "10", None):
            with self.assertRaises(ValueError):
                split_bill(100, 2, bad)


if __name__ == "__main__":
    unittest.main()
