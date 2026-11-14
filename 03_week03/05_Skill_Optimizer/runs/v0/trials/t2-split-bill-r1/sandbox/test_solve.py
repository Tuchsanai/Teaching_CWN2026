import unittest
from solve import split_bill, main


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_rounding(self):
        # tip = 0.5 -> 1
        self.assertEqual(split_bill(5, 1, 10), [6])
        self.assertEqual(split_bill(4, 1, 10), [4])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum(self):
        r = split_bill(99999, 7, 15)
        self.assertEqual(sum(r), 99999 + (99999 * 15 + 50) // 100)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.5, 1, 0), (1, True, 0), ("1", 1, 0), (1, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        self.assertEqual(main(['{"total":1000,"people":3,"tip_percent":0}']), 0)
        self.assertEqual(main(['{"total":1000}']), 1)
        self.assertEqual(main(['not json']), 1)


if __name__ == "__main__":
    unittest.main()
