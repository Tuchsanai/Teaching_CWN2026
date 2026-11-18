import unittest
from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_rounding_half_up(self):
        # tip = 5*10/100 = 0.5 -> 1
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 15)
        self.assertEqual(sum(r), 9999 + (9999 * 15 + 50) // 100)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.5, 1, 0), (True, 1, 0), (1, 1, "5"), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
