import unittest

from solve import late_fee as fn


class Normal(unittest.TestCase):
    def test_no_fee_zero_days(self):
        self.assertEqual(fn(100000, 0), 0)

    def test_four_days(self):  # 100000*0.0075*4 = 3000
        self.assertEqual(fn(100000, 4), 3000)

    def test_ten_days(self):  # 20000*0.0075*10 = 1500
        self.assertEqual(fn(20000, 10), 1500)

    def test_zero_amount(self):
        self.assertEqual(fn(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(fn(100000, 3), 0)
        self.assertEqual(fn(100000, 4), 3000)
        self.assertEqual(fn(100000, 2), 0)

    def test_cap_edge(self):  # 20 วัน = 15% พอดี
        self.assertEqual(fn(100000, 19), 14250)
        self.assertEqual(fn(100000, 20), 15000)
        self.assertEqual(fn(100000, 21), 15000)

    def test_range_limits(self):
        self.assertEqual(fn(100000, 365), 15000)
        self.assertEqual(fn(0, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half_exact_up(self):  # 10*0.0075*4=0.3 -> 0 ; 200*.0075*4=6 ; 10*.0075*... 
        self.assertEqual(fn(50, 4), 2)    # 1.5 -> 2

    def test_below_half_down(self):
        self.assertEqual(fn(10, 4), 0)    # 0.3 -> 0
        self.assertEqual(fn(110, 5), 4)   # 4.125 -> 4

    def test_above_half_up(self):
        self.assertEqual(fn(70, 10), 5)   # 5.25 -> 5
        self.assertEqual(fn(90, 10), 7)   # 6.75 -> 7

    def test_cap_fraction(self):  # cap 15% ของ 10 = 1.5 -> 2
        self.assertEqual(fn(10, 365), 2)
        self.assertEqual(fn(30, 365), 5)  # 4.5 -> 5


class Reject(unittest.TestCase):
    def test_reject_amount(self):
        for bad in (-1, 1.0, "100", True, None, [1]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                fn(bad, 5)

    def test_reject_days(self):
        for bad in (-1, 366, 5.0, "5", True, False, None, [1]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                fn(1000, bad)


if __name__ == "__main__":
    unittest.main()
