"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):  # 10000*0.0075*10 = 750
        self.assertEqual(late_fee(10000, 10), 750)

    def test_normal_2(self):  # 200000*0.0075*5 = 7500
        self.assertEqual(late_fee(200000, 5), 7500)

    def test_normal_3(self):  # 50000*0.0075*15 = 5625
        self.assertEqual(late_fee(50000, 15), 5625)


class Boundary(unittest.TestCase):
    def test_boundary_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_boundary_4_days(self):  # 100000*0.03 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_boundary_cap(self):  # 20 วัน = 15% พอดี, 21+ ติดเพดาน
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_boundary_zero(self):
        self.assertEqual(late_fee(0, 100), 0)
        self.assertEqual(late_fee(100000, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # 100*0.0075*4 = 3.0 ; 50*0.0075*4=1.5 -> 2
        self.assertEqual(late_fee(100, 4), 3)
        self.assertEqual(late_fee(50, 4), 2)

    def test_fraction_down(self):  # 33*0.0075*4 = 0.99 -> 1 ; 10*0.0075*5=0.375 -> 0
        self.assertEqual(late_fee(33, 4), 1)
        self.assertEqual(late_fee(10, 5), 0)

    def test_odd(self):  # 12345*0.0075*7 = 648.1125 -> 648
        self.assertEqual(late_fee(12345, 7), 648)


class Reject(unittest.TestCase):
    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)
        with self.assertRaises(ValueError):
            late_fee(100, -1)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            late_fee(100, 366)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)
        with self.assertRaises(ValueError):
            late_fee(100, 5.0)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            late_fee("100", 5)

    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)
        with self.assertRaises(ValueError):
            late_fee(100, True)


if __name__ == "__main__":
    unittest.main()
