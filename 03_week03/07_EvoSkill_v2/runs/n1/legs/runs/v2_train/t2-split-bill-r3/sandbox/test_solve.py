import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(5, 1, 100), [10])
        self.assertEqual(split_bill(100, 1, 0), [100])

    def test_nodrift(self):
        # 101*1.05=106.05 -> 106 ; 105*1.10=115.5 -> 116
        self.assertEqual(split_bill(101, 1, 5), [106])
        self.assertEqual(split_bill(105, 1, 10), [116])
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 11299)
        self.assertEqual(r, sorted(r, reverse=True))

    def test_reject(self):
        bad = [(-1, 2, 0), (100.0, 2, 0), ("100", 2, 0), (True, 2, 0), (None, 2, 0),
               (100, 0, 0), (100, -1, 0), (100, 2.0, 0), (100, True, 0), (100, "2", 0),
               (100, 2, -1), (100, 2, 101), (100, 2, 5.0), (100, 2, True), (100, 2, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
