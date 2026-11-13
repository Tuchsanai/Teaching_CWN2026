import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(0, 2, 50), [0, 0])

    def test_boundary(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_half_up(self):
        # 50*1.01=50.5 -> 51 (floor would give 50)
        self.assertEqual(split_bill(50, 1, 1), [51])
        self.assertEqual(sum(split_bill(12345, 7, 7)), 13209)

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, True, 0), (1, 1, 5.0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
