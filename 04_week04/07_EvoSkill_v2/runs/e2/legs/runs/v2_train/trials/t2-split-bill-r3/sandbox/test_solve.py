import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(100, 1, 0), [100])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 2, 100), [100, 100])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_nodrift(self):
        self.assertEqual(sum(split_bill(12345, 7, 15)), 14197)  # 14196.75
        self.assertEqual(split_bill(10, 1, 5), [11])  # 10.5 -> 11
        self.assertEqual(split_bill(999999999, 3, 7), [356666667, 356666666, 356666666])

    def test_reject(self):
        for a in [(-1, 2, 0), (100, 0, 0), (100, 2, -1), (100, 2, 101),
                  (100.0, 2, 0), (100, 2.0, 0), (100, 2, 10.5), ("1", 2, 0),
                  (True, 2, 0), (100, True, 0), (100, 2, None)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
