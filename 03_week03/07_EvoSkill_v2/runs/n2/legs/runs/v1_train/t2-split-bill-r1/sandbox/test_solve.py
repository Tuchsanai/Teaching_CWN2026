import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(1000, 1, 0), [1000])
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_half_up(self):
        # 105*110/100 = 115.5 -> 116
        self.assertEqual(sum(split_bill(105, 2, 10)), 116)

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, 1, None), (1, 2.0, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
