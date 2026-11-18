import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(5, 3, 0), [2, 2, 1])

    def test_nodrift(self):
        # 15*107/100 ... half-up: 1050*1.05=1102.5 -> 1103
        self.assertEqual(split_bill(1050, 1, 5), [1103])
        r = split_bill(999999999999, 7, 13)
        self.assertEqual(sum(r), (999999999999 * 113 * 2 + 100) // 200)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                  (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0),
                  (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
