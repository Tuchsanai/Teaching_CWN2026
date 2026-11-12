import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_boundary_below(self):
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_boundary_at(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_half_up(self):
        # 1 * 150/100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 201*1.05 = 211.05 -> 211 ; 2 people
        self.assertEqual(split_bill(201, 2, 5), [106, 105])

    def test_reject_range(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_float(self):
        for a in [(10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_bool_or_type(self):
        for a in [(True, 1, 0), (10, True, 0), (10, 1, False), ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_combined(self):
        r = split_bill(9999, 7, 12)
        self.assertEqual(sum(r), 11199)
        self.assertLessEqual(max(r) - min(r), 1)


if __name__ == "__main__":
    unittest.main()
