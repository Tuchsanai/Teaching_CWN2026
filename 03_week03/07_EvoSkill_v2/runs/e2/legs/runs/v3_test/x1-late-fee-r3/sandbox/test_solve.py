import unittest
from fractions import Fraction
from solve import late_fee


def ref(a, d):
    if d <= 3:
        return 0
    f = min(Fraction(a) * 75 * d / 10000, Fraction(a) * 15 / 100)
    return int((f * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(0, 10), 0)
        self.assertEqual(late_fee(25075, 7), ref(25075, 7))


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(5333, 365), ref(5333, 365))


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 200*0.0075*4 = 6.0; 10*.0075*... use .5 cases
        self.assertEqual(late_fee(10, 10), 1)      # 0.75 -> 1
        self.assertEqual(late_fee(2000, 5), 75)    # 75.0
        self.assertEqual(late_fee(10, 20), 2)      # cap 1.5 -> 2
        self.assertEqual(late_fee(30, 5), 1)       # 1.125 -> 1
        self.assertEqual(late_fee(200, 5), 8)      # 7.5 -> 8
        self.assertEqual(late_fee(5001, 6), ref(5001, 6))

    def test_all(self):
        for a in (1, 7, 133, 5001, 25075):
            for d in range(0, 366):
                self.assertEqual(late_fee(a, d), ref(a, d))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [1.0, "1", True, None, -1, [], 1000.5]
        for v in bad:
            with self.assertRaises(ValueError):
                late_fee(v, 5)
            with self.assertRaises(ValueError):
                late_fee(1000, v)
        for d in (-1, 366):
            with self.assertRaises(ValueError):
                late_fee(1000, d)


if __name__ == "__main__":
    unittest.main()
