import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 1001*1.05 = 1051.05 -> 1051 ; 10*1.05=10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(1001, 1, 5), [1051])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_edges(self):
        self.assertEqual(sum(split_bill(999, 7, 100)), 1998)
        self.assertEqual(split_bill(5, 1, 100), [10])

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                  (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                  (True, 1, 0), (10, True, 0), (10, 1, False), ("1", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
