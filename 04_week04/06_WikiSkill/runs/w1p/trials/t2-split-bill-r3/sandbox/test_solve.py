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
        self.assertEqual(split_bill(1000, 5, 100), [400] * 5)

    def test_fewer_satang_than_people(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_tip_rounding_half_up(self):
        # ทิป 5% ของ 10 = 0.5 -> ปัดขึ้น 1 (ข้อสมมติ) => 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # ทิป 5% ของ 9 = 0.45 -> 0 => 9
        self.assertEqual(split_bill(9, 1, 5), [9])

    def test_sum_and_int(self):
        r = split_bill(12345, 7, 15)
        self.assertEqual(sum(r), 12345 + 1852)  # 1851.75 -> 1852
        for x in r:
            self.assertIs(type(x), int)

    def test_reject_total(self):
        for v in (-1, 10.0, True, "10", None):
            with self.assertRaises(ValueError):
                split_bill(v, 2, 0)

    def test_reject_people(self):
        for v in (0, -1, 2.0, True, "2", None):
            with self.assertRaises(ValueError):
                split_bill(100, v, 0)

    def test_reject_tip_percent(self):
        for v in (-1, 101, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                split_bill(100, 2, v)


if __name__ == "__main__":
    unittest.main()
