import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_more_people_than_money(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1), (10, 1, 101),
                  (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), (True, 1, 0),
                  (10, True, 0), (10, 1, True), ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
