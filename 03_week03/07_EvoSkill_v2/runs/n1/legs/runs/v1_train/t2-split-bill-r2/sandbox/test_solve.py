import unittest
from fractions import Fraction
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])
        self.assertEqual(split_bill(10, 3, 0), [4, 3, 3])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(0, 3, 100), [0, 0, 0])
        self.assertEqual(split_bill(500, 1, 100), [1000])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_nodrift(self):
        # 1005*5% = 50.25 ; 1 -> 10*15% =1.5 -> total 11.5 -> 12
        self.assertEqual(sum(split_bill(10, 1, 15)), 12)
        self.assertEqual(sum(split_bill(1005, 1, 5)), 1055)
        for t in (1, 7, 99, 12345):
            for p in (1, 3, 7):
                for tip in (0, 5, 12, 33, 100):
                    r = split_bill(t, p, tip)
                    g = Fraction(t) * (100 + tip) / 100
                    exp = int((g * 2 + 1) // 2)
                    self.assertEqual(sum(r), exp)
                    self.assertTrue(all(type(x) is int for x in r))
                    self.assertLessEqual(max(r) - min(r), 1)
                    self.assertEqual(r, sorted(r, reverse=True))

    def test_reject(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
               (4500.0, 1, 0), (1, 2.0, 0), (1, 1, 5.0), ('3', 1, 0),
               (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]
        for a in bad:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
