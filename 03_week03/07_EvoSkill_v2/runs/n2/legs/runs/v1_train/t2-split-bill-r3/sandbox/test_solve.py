import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(100, 2, 100), [100, 100])

    def test_half_up(self):
        # 10 * 1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(sum(split_bill(999, 7, 15)), 1149)  # 1148.85 -> 1149

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, True, 0), (1, 1, None), (1, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
