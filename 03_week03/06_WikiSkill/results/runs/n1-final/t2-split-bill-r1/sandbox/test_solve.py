import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)

    def test_boundary_below(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])

    def test_boundary_at(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_half_up(self):
        # 501*1.10 = 551.1 -> 551 ; 505*1.1=555.5 -> 556
        self.assertEqual(split_bill(505, 1, 10), [556])

    def test_remainder_order(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(sum(split_bill(9999, 7, 15)), 11499)

    def test_reject_range(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_float(self):
        for a in [(1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_bool_or_type(self):
        for a in [(True, 1, 0), (1, True, 0), (1, 1, False), ("1", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
