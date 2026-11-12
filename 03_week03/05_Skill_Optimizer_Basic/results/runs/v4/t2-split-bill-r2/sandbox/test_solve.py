import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 1, 10), [1100])

    def test_half_up_once(self):
        self.assertEqual(split_bill(5, 1, 10), [6])   # 5.5 -> 6
        self.assertEqual(split_bill(1, 1, 49), [1])   # 1.49 -> 1
        self.assertEqual(split_bill(1, 1, 50), [2])   # 1.5 -> 2

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_sum_and_len(self):
        r = split_bill(9999, 7, 15)
        self.assertEqual(len(r), 7)
        self.assertEqual(sum(r), (9999 * 115 + 50) // 100)

    def test_invalid(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                  (1.0, 1, 0), (1, True, 0), ("1", 1, 0), (1, 1, 5.0), (True, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
