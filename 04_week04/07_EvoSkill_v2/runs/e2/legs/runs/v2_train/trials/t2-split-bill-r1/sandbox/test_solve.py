import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])
        self.assertEqual(split_bill(1000, 1, 0), [1000])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_nodrift(self):
        r = split_bill(999999999999, 7, 15)
        self.assertEqual(sum(r), (999999999999 * 115 * 2 + 100) // 200)
        self.assertEqual(split_bill(5, 1, 10), [6])  # 5.5 -> 6
        self.assertTrue(all(type(x) is int for x in r))

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, 1, 5.0), (1, None, 0), (1, 1, True)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
