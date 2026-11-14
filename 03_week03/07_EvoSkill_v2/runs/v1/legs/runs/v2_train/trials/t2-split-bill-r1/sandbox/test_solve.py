import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10001, 3, 0), [3334, 3334, 3333])

    def test_tip_rounding(self):
        self.assertEqual(split_bill(1005, 1, 10), [1106])  # 1105.5 -> 1106
        self.assertEqual(sum(split_bill(9999, 7, 15)), 11499)

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, None, 0), (1, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


unittest.main() if __name__ == "__main__" else None
