import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_remainder_goes_to_first(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_with_tip(self):
        # 1000 + 10% = 1100 ; 1100 = 366*3 + 2
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_single_person(self):
        self.assertEqual(split_bill(1000, 1, 10), [1100])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 2, 50), [0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_tip_100_percent(self):
        self.assertEqual(split_bill(500, 2, 100), [500, 500])

    def test_tip_rounding_half_up(self):
        # ข้อสมมติ: 5 * 1.10 = 5.5 -> ปัดครึ่งขึ้นเป็น 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1 * 1.40 = 1.4 -> 1
        self.assertEqual(split_bill(1, 1, 40), [1])

    def test_result_is_int_and_sums(self):
        r = split_bill(9999, 7, 15)
        self.assertTrue(all(type(x) is int for x in r))
        self.assertEqual(len(r), 7)
        self.assertEqual(sum(r), (9999 * 115 * 2 + 100) // 200)

    def test_reject_total(self):
        for v in (-1, 10.0, True, "100", None):
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
