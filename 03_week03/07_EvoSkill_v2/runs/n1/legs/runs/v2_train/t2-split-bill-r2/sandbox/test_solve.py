import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(0, 2, 50), [0, 0])

    def test_boundary(self):
        self.assertEqual(split_bill(1, 1, 100), [2])
        self.assertEqual(split_bill(5, 3, 0), [2, 2, 1])

    def test_nodrift(self):
        # 105*1.10=115.5 -> 116 (half-up)
        self.assertEqual(split_bill(105, 1, 10), [116])
        self.assertEqual(sum(split_bill(9999, 7, 13)), round(9999 * 1.13 + 1e-9))

    def test_reject(self):
        bad = [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
               (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), ("10", 1, 0),
               (True, 1, 0), (10, True, 0), (10, 1, True), (None, 1, 0)]
        for a in bad:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
