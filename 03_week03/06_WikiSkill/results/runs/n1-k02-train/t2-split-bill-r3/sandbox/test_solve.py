import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 1, 10), [1100])

    def test_half_up(self):
        # 25 * 110% = 27.5 -> 28
        self.assertEqual(split_bill(25, 1, 10), [28])
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_edges(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(100, 1, 0), [100])
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_types(self):
        for args in [(10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), (True, 1, 0),
                     (10, True, 0), (10, 1, False), ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
