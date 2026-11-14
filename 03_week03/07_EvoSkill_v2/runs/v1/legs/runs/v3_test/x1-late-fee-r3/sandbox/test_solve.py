import unittest
from fractions import Fraction
from solve import late_fee


def ref(a, d):
    if d <= 3:
        return 0
    f = min(Fraction(75, 10000) * d, Fraction(15, 100)) * a
    return int((f * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(late_fee(200, 4), 6)      # 6.0
        self.assertEqual(late_fee(10, 10), 1)      # 0.75 -> 1
        self.assertEqual(late_fee(2, 4), 0)        # 0.06
        for a in range(0, 3000, 7):
            for d in (0, 3, 4, 5, 13, 19, 20, 21, 365):
                self.assertEqual(late_fee(a, d), ref(a, d))


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (1000.0, 5), ("1000", 5),
                     (True, 5), (100, 5.0), (100, "5"), (100, True),
                     (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
