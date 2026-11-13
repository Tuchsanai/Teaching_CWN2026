import unittest
from fractions import Fraction
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(500, 1, 100), [1000])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_nodrift(self):
        # 150*1.05 = 157.5 -> 158 (half-up)
        self.assertEqual(sum(split_bill(150, 2, 5)), 158)
        for total in range(0, 400, 7):
            for p in (1, 2, 3, 7):
                for tip in (0, 5, 10, 15, 33, 100):
                    g = Fraction(total * (100 + tip), 100)
                    exp = int((g * 2 + 1) // 2)
                    r = split_bill(total, p, tip)
                    self.assertEqual(sum(r), exp)
                    self.assertEqual(len(r), p)
                    self.assertLessEqual(max(r) - min(r), 1)
                    self.assertEqual(r, sorted(r, reverse=True))
                    self.assertTrue(all(type(x) is int for x in r))

    def test_reject(self):
        bad = [(-1, 2, 0), (100, 0, 0), (100, -1, 0), (100, 2, -1), (100, 2, 101),
               (100.0, 2, 0), (100, 2.0, 0), (100, 2, 10.0), ("100", 2, 0),
               (100, "2", 0), (100, 2, "10"), (True, 2, 0), (100, True, 0),
               (100, 2, True), (None, 2, 0), (100, None, 0), (100, 2, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
