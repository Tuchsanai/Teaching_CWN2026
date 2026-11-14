import unittest
from fractions import Fraction
from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(20000, 4), 600)
        self.assertEqual(late_fee(0, 100), 0)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_nodrift(self):
        for a in (1, 2, 66, 67, 133, 999, 12345):
            for d in range(0, 366):
                f = min(Fraction(a * 75 * d, 10000), Fraction(a * 15, 100)) if d > 3 else 0
                self.assertEqual(late_fee(a, d), int((Fraction(f) * 2 + 1) // 2))
        self.assertEqual(late_fee(200, 5), 8)   # 7.5 -> 8
        self.assertEqual(late_fee(2, 4), 0)

    def test_reject(self):
        for a, d in [(-1, 5), (1000, -1), (1000, 366), (1000.0, 5), ("1000", 5),
                     (True, 5), (1000, 5.0), (1000, "5"), (1000, True), (None, 5),
                     (1000, None), (float("nan"), 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
