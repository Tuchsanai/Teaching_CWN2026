import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(1, 1, 0), [1])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_half_up(self):
        # 10 * 1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 30 * 1.05 = 31.5 -> 32
        self.assertEqual(split_bill(30, 1, 5), [32])
        # 9 * 1.05 = 9.45 -> 9
        self.assertEqual(split_bill(9, 1, 5), [9])

    def test_reject(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, -1, 0), (100, 1, -1),
                     (100, 1, 101), (100.0, 1, 0), (100, 1.0, 0),
                     (100, 1, 10.0), (True, 1, 0), (100, True, 0),
                     (100, 1, True), ("100", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
