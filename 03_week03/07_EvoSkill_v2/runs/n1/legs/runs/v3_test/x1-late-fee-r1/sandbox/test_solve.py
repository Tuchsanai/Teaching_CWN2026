import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_4_days(self):  # 100000*0.03 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_10_days(self):  # 100000*0.075 = 7500
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap(self):  # 15% = 15000
        self.assertEqual(late_fee(100000, 30), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(late_fee(10000, 3), 0)
        self.assertEqual(late_fee(10000, 4), 300)

    def test_cap_edge(self):  # 20 วัน = 15% พอดี
        self.assertEqual(late_fee(10000, 19), 1425)  # 14.25%
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 21), 1500)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_max_days(self):
        self.assertEqual(late_fee(333, 365), 50)  # 49.95 -> 50


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # 100*0.03=3 ; 50*0.03=1.5 -> 2 (floor 1, even 2)
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(150, 4), 5)  # 4.5 -> 5 (even would be 4)

    def test_below_half(self):  # 49*0.03 = 1.47 -> 1
        self.assertEqual(late_fee(49, 4), 1)

    def test_fraction(self):  # 1234*0.0375 (5 วัน) = 46.275 -> 46
        self.assertEqual(late_fee(1234, 5), 46)
        self.assertEqual(late_fee(1234567, 7), 64815)  # 64814.8 -> 64815


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            late_fee(*a)

    def test_amount(self):
        for v in (-1, 1.5, 100.0, "100", True, None):
            self.bad(v, 5)
            self.bad(v, 0)  # ผิดแม้ไป early-return

    def test_days(self):
        for v in (-1, 366, 5.0, 4.5, "5", True, False, None):
            self.bad(1000, v)


if __name__ == "__main__":
    unittest.main()
