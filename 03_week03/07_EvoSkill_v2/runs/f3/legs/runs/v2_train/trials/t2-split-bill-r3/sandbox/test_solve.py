import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 7, 10), [1572, 1572, 1572, 1571, 1571, 1571, 1571])

    def test_boundary(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])
        self.assertEqual(split_bill(0, 2, 100), [0, 0])
        self.assertEqual(split_bill(5, 1, 10), [6])  # 5.5 -> 6

    def test_nodrift(self):
        for t, p, tip in [(9999, 7, 13), (1, 5, 100), (123457, 11, 7)]:
            r = split_bill(t, p, tip)
            self.assertEqual(len(r), p)
            self.assertLessEqual(max(r) - min(r), 1)

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, -2, 0), (1, '3', 0), (1.0, 1, 0),
                  (True, 1, 0), (1, 1, 101), (1, 1, -1), (1, 1, 5.0), (1, 1, None)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
