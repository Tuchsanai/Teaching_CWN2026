import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_half_up_once(self):
        # 105*1.10=115.5 -> 116 ; 1 person
        self.assertEqual(split_bill(105, 1, 10), [116])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), (9999 * 113 + 50) // 100)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_invalid(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                  (1.0, 1, 0), (True, 1, 0), (1, "2", 0), (1, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
