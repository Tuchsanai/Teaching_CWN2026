import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])  # 11000
    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1, 5, 0), [1, 0, 0, 0, 0])
        self.assertEqual(len(split_bill(10, 1000, 0)), 1000)
    def test_nodrift(self):
        self.assertEqual(split_bill(10, 1, 5), [11])   # 10.5 -> 11
        self.assertEqual(split_bill(30, 1, 5), [32])   # 31.5 -> 32
        self.assertEqual(split_bill(1, 1, 49), [1])    # 1.49 -> 1
        for t, p, tip in [(9999, 7, 13), (12345, 6, 7)]:
            r = split_bill(t, p, tip)
            self.assertEqual(sum(r), (t * (100 + tip) * 2 + 100) // 200)
            self.assertLessEqual(max(r) - min(r), 1)
    def test_reject(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, -1, 0), (1, 1, -1), (1, 1, 101),
               (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0), (1, "1", 0),
               (1, 1, "5"), (True, 1, 0), (1, True, 0), (1, 1, True),
               (None, 1, 0), (1, None, 0), (1, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
