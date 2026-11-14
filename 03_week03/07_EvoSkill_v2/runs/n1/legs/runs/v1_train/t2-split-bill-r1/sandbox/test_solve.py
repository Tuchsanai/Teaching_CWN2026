import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_nodrift(self):
        self.assertEqual(split_bill(1, 1, 50), [2])  # 1.5 -> 2
        r = split_bill(999, 7, 7)
        self.assertEqual(sum(r), 1069)  # 1068.93
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (True, 1, 0),
                  (1.0, 1, 0), (1, "2", 0), (1, 1, 5.0), (1, True, 0), (1, 1, None)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
