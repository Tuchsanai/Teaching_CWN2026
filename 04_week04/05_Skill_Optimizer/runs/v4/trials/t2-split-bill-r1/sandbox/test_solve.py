import unittest
from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_tip_round_half_up(self):
        # 5*10% = 0.5 -> 1
        self.assertEqual(sum(split_bill(5, 1, 10)), 6)

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 9999 + (9999 * 13 + 50) // 100)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_invalid(self):
        for args in [(1.5, 1, 0), (10, 0, 0), (-1, 1, 0), (10, 1, 101), (True, 1, 0), (10, "2", 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
