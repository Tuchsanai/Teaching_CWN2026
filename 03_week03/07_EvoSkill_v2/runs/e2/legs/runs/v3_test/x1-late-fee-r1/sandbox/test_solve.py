import unittest
from fractions import Fraction
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(5001, 7), 263)  # 262.55 -> 263

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_within_grace(self):
        for d in (0, 1, 2, 3):
            self.assertEqual(late_fee(123457, d), 0)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(late_fee(10000, 3), 0)
        self.assertEqual(late_fee(10000, 4), 300)
        self.assertEqual(late_fee(10000, 5), 375)

    def test_cap_edge(self):
        self.assertEqual(late_fee(10000, 19), 1425)
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)
        self.assertEqual(late_fee(25075, 365), 3761)  # 3761.25 cap

    def test_days_range(self):
        late_fee(1, 0)
        late_fee(1, 365)


class NoDrift(unittest.TestCase):
    def exp(self, a, d):
        if d <= 3:
            return 0
        v = min(Fraction(a) * Fraction(75, 10000) * d, Fraction(a) * Fraction(15, 100))
        return int((v * 2 + 1) // 2)

    def test_half_exact_up(self):
        # 200*0.0075*5 = 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        # 1000*0.0075*5 = 37.5 -> 38
        self.assertEqual(late_fee(1000, 5), 38)
        # cap 15% of 10 = 1.5 -> 2
        self.assertEqual(late_fee(10, 365), 2)

    def test_round_down_case(self):
        # 5333*0.0075*4 = 159.99 -> 160 ; 5001*.0075*4=150.03 -> 150
        self.assertEqual(late_fee(5001, 4), 150)
        self.assertEqual(late_fee(5333, 4), 160)

    def test_sweep(self):
        for a in (1, 7, 133, 5001, 5333, 25075, 99999999):
            for d in range(0, 366, 1):
                self.assertEqual(late_fee(a, d), self.exp(a, d), (a, d))

    def test_big(self):
        self.assertEqual(late_fee(10**15 + 1, 10), self.exp(10**15 + 1, 10))


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            late_fee(*a)

    def test_amount(self):
        for v in (-1, 1000.0, "1000", True, False, None, [1]):
            self.bad(v, 5)

    def test_days(self):
        for v in (-1, 366, 5.0, "5", True, False, None, 1000):
            self.bad(1000, v)

    def test_both(self):
        self.bad(None, None)
        self.bad(-1, -1)

    def test_invalid_even_in_grace(self):
        self.bad(-5, 0)
        self.bad(1000, 366)


if __name__ == "__main__":
    unittest.main()
