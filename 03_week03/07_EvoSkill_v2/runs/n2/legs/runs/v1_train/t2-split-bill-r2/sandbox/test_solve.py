import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(0, 2, 0), [0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_half(self):
        # 1 * 150/100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 3 * 1.5 = 4.5 -> 5
        self.assertEqual(split_bill(3, 2, 50), [3, 2])

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, 1, None), (1, 2.0, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
