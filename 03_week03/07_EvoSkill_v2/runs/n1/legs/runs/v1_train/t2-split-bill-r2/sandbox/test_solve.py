import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(5, 2, 0), [3, 2])

    def test_nodrift(self):
        # 1 * 1.05 = 1.05 -> 1 ; 10*1.05=10.5 -> 11 (half-up)
        self.assertEqual(split_bill(10, 1, 5), [11])
        r = split_bill(99999, 7, 13)
        self.assertEqual(sum(r), 112999)  # 99999*1.13=112998.87
        self.assertLessEqual(max(r) - min(r), 1)

    def test_reject(self):
        bad = [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
               (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), ("10", 1, 0),
               (True, 1, 0), (10, True, 0), (10, 1, True), (None, 1, 0)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
