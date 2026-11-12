import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_boundary_exact(self):
        self.assertEqual(split_bill(1000, 1, 100), [2000])

    def test_boundary_below(self):
        self.assertEqual(split_bill(0, 1, 0), [0])

    def test_boundary_above(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_half_up(self):
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1*150/100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 2, 50), [1, 1])

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
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])


if __name__ == "__main__":
    unittest.main()
