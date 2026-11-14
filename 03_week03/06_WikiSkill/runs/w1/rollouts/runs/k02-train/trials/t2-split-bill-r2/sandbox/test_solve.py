import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_edges(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1, 1, 0), [1])
        # ทิปปัดครึ่งขึ้น: 10*5/100=0.5 -> 1
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(10, 1, 4), [10])

    def test_reject(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, -1, 0), (100, 1, -1),
                     (100, 1, 101), (100.0, 1, 0), (100, 1.0, 0),
                     (100, 1, 10.0), (True, 1, 0), (100, True, 0),
                     (100, 1, True), ("100", 1, 0), (None, 1, 0)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
