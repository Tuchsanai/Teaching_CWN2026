import unittest
from solve import split_bill, main


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_rounding(self):
        # 105*10% = 10.5 -> 11 ; 116 / 3
        self.assertEqual(split_bill(105, 3, 10), [39, 39, 38])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 9999 + (9999 * 13 + 50) // 100)

    def test_invalid(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                  (1.5, 1, 0), (1, 1.0, 0), (1, 1, 5.0), (True, 1, 0), ("1", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_cli(self):
        self.assertEqual(main(['{"total":100,"people":3,"tip_percent":0}']), 0)
        self.assertEqual(main(['{"total":100}']), 1)
        self.assertEqual(main(['nope']), 1)


if __name__ == "__main__":
    unittest.main()
