import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(1, 1, 100), [2])

    def test_half_up(self):
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 15*110/100 = 16.5 -> 17 ; 2 people
        self.assertEqual(split_bill(15, 2, 10), [9, 8])

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  (1, 1.0, 0), (1, 1, 1.0), ("1", 1, 0), (True, 1, 0),
                  (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
