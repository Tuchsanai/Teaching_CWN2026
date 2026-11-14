import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_nodrift(self):
        # 105*1.05 = 110.25 -> 110 ; 10*1.05=10.5 -> 11
        self.assertEqual(split_bill(105, 1, 5), [110])
        self.assertEqual(split_bill(10, 1, 5), [11])
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 11299)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.0, 1, 0), (1, 2.0, 0), (1, 1, 5.0), ("1", 1, 0),
                  (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
