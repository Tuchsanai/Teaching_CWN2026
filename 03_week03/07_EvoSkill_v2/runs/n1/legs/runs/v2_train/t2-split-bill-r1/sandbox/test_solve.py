import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_nodrift(self):
        # 1*105/100 = 1.05 -> 1 ; 10*105/100=10.5 -> 11
        self.assertEqual(split_bill(1, 1, 5), [1])
        self.assertEqual(split_bill(10, 1, 5), [11])
        r = split_bill(999, 7, 13)
        self.assertEqual(sum(r), 1129)  # 999*1.13=1128.87

    def test_reject(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
               (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0), (1, "2", 0), (True, 1, 0),
               (1, True, 0), (1, 1, True), (None, 1, 0), (1, None, 0), (1, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
