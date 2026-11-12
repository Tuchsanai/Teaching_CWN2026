import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)

    def test_boundary_below(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])

    def test_boundary_at(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(100, 1, 0), [100])

    def test_half_up(self):
        # 101 * 1.5 -> 100*... 201*1.5=301.5 -> 302
        self.assertEqual(split_bill(201, 1, 50), [302])

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])
        self.assertEqual(split_bill(5, 7, 0), [1, 1, 1, 1, 1, 0, 0])

    def test_reject_range(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_float(self):
        for a in [(100.0, 1, 0), (100, 1.0, 0), (100, 1, 10.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_reject_bool_or_type(self):
        for a in [(True, 1, 0), (100, True, 0), (100, 1, False), ("1", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
