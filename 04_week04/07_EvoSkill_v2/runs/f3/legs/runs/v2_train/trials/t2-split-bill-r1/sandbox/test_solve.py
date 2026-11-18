import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 7, 10),
                         [1572, 1572, 1572, 1571, 1571, 1571, 1571])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 2, 0), [0, 0])
        self.assertEqual(split_bill(5, 1, 100), [10])

    def test_nodrift(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])
        self.assertEqual(sum(split_bill(9999, 7, 15)), 11499)  # 11498.85 -> 11499

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, -2, 0), (1, '3', 0), (1.0, 1, 0),
                  (1, True, 0), (1, 1, 101), (1, 1, -1), (1, 1, 10.0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
