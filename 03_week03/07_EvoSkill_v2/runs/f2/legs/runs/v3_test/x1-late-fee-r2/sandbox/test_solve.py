import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)  # 0.75%*10=7.5%
    def test_cap(self):
        self.assertEqual(late_fee(100000, 30), 15000)
    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_three_days(self):
        self.assertEqual(late_fee(100000, 3), 0)
    def test_four_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)
    def test_cap_edge(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)
    def test_max_days(self):
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 200*0.0075*4 = 6.0 ; 50*0.0075*4=1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        # 10*0.0075*5=0.375 -> 0 ; 70*0.0075*5=2.625 -> 3
        self.assertEqual(late_fee(10, 5), 0)
        self.assertEqual(late_fee(70, 5), 3)
    def test_half_exact(self):
        # 10 * 0.0075 * 20 = 1.5 cap 1.5 -> 2
        self.assertEqual(late_fee(10, 20), 2)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), ("1", 5),
                     (True, 5), (100, 5.0), (100, True), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
