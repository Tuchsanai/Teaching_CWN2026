import unittest
from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 1, 10), [1100])

    def test_round_half_up(self):
        # 1 * 150 / 100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), (9999 * 113 + 50) // 100)
        self.assertEqual(len(r), 7)

    def test_invalid(self):
        for args in [(1.5, 1, 0), (10, 0, 0), (-1, 1, 0), (10, 1, 101),
                     (10, True, 0), ("10", 1, 0), (10, 1, -1)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
