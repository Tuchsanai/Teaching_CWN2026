import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(sum(split_bill(999, 7, 100)), 1998)

    def test_half_up(self):
        # 1 * 1.5 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 10*1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(1, 1, 49), [1])

    def test_reject(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                     (1000.0, 1, 0), (10, 1.0, 0), (10, 1, 10.0),
                     (True, 1, 0), (10, True, 0), ("10", 1, 0), (None, 1, 0)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
