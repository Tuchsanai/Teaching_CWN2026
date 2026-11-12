import unittest
from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(1001, 3, 0), [334, 334, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up_once(self):
        # 105*105/100 = 110.25 -> 110 ; 10*105/100 = 10.5 -> 11
        self.assertEqual(sum(split_bill(105, 1, 5)), 110)
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(len(r), 7)
        self.assertEqual(sum(r), (9999 * 113 + 50) // 100)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.5, 1, 0), (1, 1.0, 0), (1, 1, 5.0),
                     (True, 1, 0), (1, True, 0), ("1", 1, 0)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
