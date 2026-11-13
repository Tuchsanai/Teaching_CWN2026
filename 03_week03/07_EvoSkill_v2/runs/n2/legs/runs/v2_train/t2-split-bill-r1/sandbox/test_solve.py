import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(0, 2, 10), [0, 0])
        self.assertEqual(split_bill(1000, 1, 100), [2000])

    def test_half_up(self):
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1*150/100=1.5 -> 2 ; 2 คน -> [1,1]
        self.assertEqual(split_bill(1, 2, 50), [1, 1])
        # 1*105/100=1.05 -> 1
        self.assertEqual(split_bill(1, 1, 5), [1])

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("1", 1, 0), (True, 1, 0), (1, True, 0), (1, 1, 0.0),
                  (None, 1, 0), (1, [], 0), (1, 1, None)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
