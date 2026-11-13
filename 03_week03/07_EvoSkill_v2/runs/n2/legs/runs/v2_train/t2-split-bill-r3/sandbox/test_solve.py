import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)
        self.assertEqual(split_bill(0, 2, 50), [0, 0])

    def test_half_up(self):
        # 1005*1.10 = 1105.5 -> 1106
        self.assertEqual(sum(split_bill(1005, 1, 10)), 1106)
        # 1 * 1.5 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, 1.0, 0), (1, True, 0),
                  (1, 1, None), (1, 1, 1.5), (None, 1, 0), ([], 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
