import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(1, 1, 100), [2])

    def test_half_up(self):
        # 15*1.10 = 16.5 -> 17
        self.assertEqual(split_bill(15, 1, 10), [17])
        self.assertEqual(sum(split_bill(999, 7, 7)), 1069)

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("3", 1, 0), (True, 1, 0), (1, True, 0), (1, 1, None),
                  (1, 1, float("nan")), (1, 1.0, 0), (1, -2, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_big(self):
        self.assertEqual(sum(split_bill(10**12, 7, 100)), 2 * 10**12)


if __name__ == "__main__":
    unittest.main()
