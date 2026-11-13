import unittest
from solve import split_bill, main


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_tip_rounding(self):
        # 5*10/100 = 0.5 -> rounds up to 1
        self.assertEqual(split_bill(5, 1, 10), [6])
        self.assertEqual(split_bill(4, 1, 10), [4])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum(self):
        r = split_bill(99999, 7, 15)
        self.assertEqual(sum(r), 99999 + (99999 * 15 + 50) // 100)

    def test_invalid(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.5, 1, 0), (1, 1.0, 0), (1, 1, "5"), (True, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_cli(self):
        self.assertEqual(main(['{"total":100,"people":3,"tip_percent":0}']), 0)
        self.assertEqual(main(['{"total":100}']), 1)
        self.assertEqual(main(['not json']), 1)


if __name__ == "__main__":
    unittest.main()
