import unittest
from fractions import Fraction
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(999, 1, 0), [999])
        self.assertEqual(split_bill(1000, 1, 100), [2000])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_nodrift(self):
        for total in (5, 15, 25, 999, 12345):
            for tip in (0, 5, 10, 15, 33, 100):
                for p in (1, 2, 3, 7):
                    r = split_bill(total, p, tip)
                    exact = Fraction(total * (100 + tip), 100)
                    want = int((exact * 2 + 1) // 2)
                    self.assertEqual(sum(r), want)
                    self.assertLessEqual(max(r) - min(r), 1)
                    self.assertEqual(r, sorted(r, reverse=True))
                    self.assertTrue(all(type(x) is int for x in r))
        self.assertEqual(split_bill(5, 1, 10), [6])  # 5.5 -> 6

    def test_reject(self):
        bad = [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1), (10, 1, 101),
               (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), ("10", 1, 0),
               (True, 1, 0), (10, True, 0), (10, 1, True), (None, 1, 0)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
