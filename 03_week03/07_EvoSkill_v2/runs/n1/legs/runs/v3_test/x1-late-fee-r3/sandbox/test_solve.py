import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_no_fee_within_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_counts_all_days_including_first_three(self):
        # 4 วัน = 3.00% ของ 100000 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)
        # 10 วัน = 7.5% ของ 200000 = 15000
        self.assertEqual(late_fee(200000, 10), 15000)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(late_fee(10000, 3), 0)
        self.assertEqual(late_fee(10000, 4), 300)

    def test_cap_edge(self):
        # 19 วัน = 14.25% ; 20 วัน = 15% พอดี ; 21 วัน ชนเพดาน 15%
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_max_days(self):
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 4 วัน 3% ของ 50 = 1.5 -> 2 (floor=1, half-even=2)
        self.assertEqual(late_fee(50, 4), 2)
        # 3% ของ 150 = 4.5 -> 5 (half-even จะได้ 4)
        self.assertEqual(late_fee(150, 4), 5)
        # 3% ของ 49 = 1.47 -> 1
        self.assertEqual(late_fee(49, 4), 1)
        # 5 วัน 3.75% ของ 40 = 1.5 -> 2
        self.assertEqual(late_fee(40, 5), 2)

    def test_cap_rounding(self):
        # 15% ของ 10 = 1.5 -> 2
        self.assertEqual(late_fee(10, 30), 2)
        # 15% ของ 3 = 0.45 -> 0
        self.assertEqual(late_fee(3, 30), 0)


class Reject(unittest.TestCase):
    def check(self, *args):
        with self.assertRaises(ValueError):
            late_fee(*args)

    def test_amount(self):
        for bad in (-1, 1.5, 100.0, "100", True, None):
            self.check(bad, 5)

    def test_days(self):
        for bad in (-1, 366, 5.0, 4.5, "5", True, False, None):
            self.check(1000, bad)

    def test_invalid_even_when_no_fee(self):
        self.check(-1, 0)
        self.check(1000, -1)
        self.check(1000.0, 2)


if __name__ == "__main__":
    unittest.main()
