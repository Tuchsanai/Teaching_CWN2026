import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)

    def test_boundary_exact(self):
        self.assertEqual(split_bill(100, 1, 0), [100])

    def test_boundary_below(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_boundary_above(self):
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_half_up(self):
        # 5*1.10 = 5.5 -> 6 ; split in 2
        self.assertEqual(split_bill(5, 2, 10), [3, 3])
        # 1*1.5 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])

    def test_reject_value(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_type(self):
        for a in [(10.0, 1, 0), (10, True, 0), ("10", 1, 0), (10, 1, None)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_zero_or_cap(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
