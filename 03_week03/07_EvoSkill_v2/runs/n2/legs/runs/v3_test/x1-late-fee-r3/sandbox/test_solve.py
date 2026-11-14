"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(100000, 10), 7500)  # 1000*0.075 = 75 บาท

    def test_normal_2(self):
        self.assertEqual(late_fee(200000, 5), 7500)  # 200000*0.0375

    def test_normal_3(self):
        self.assertEqual(late_fee(0, 30), 0)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)  # นับรวม 3 วันแรก

    def test_cap_edge(self):
        self.assertEqual(late_fee(100000, 20), 15000)  # 20*0.75% = 15% พอดี
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 21), 15000)  # ติดเพดาน

    def test_range_edge(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_rounds_up(self):
        self.assertEqual(late_fee(200, 5), 8)  # 7.5 -> 8

    def test_fraction_up(self):
        self.assertEqual(late_fee(50, 5), 2)  # 1.875 -> 2

    def test_fraction_down(self):
        self.assertEqual(late_fee(10, 4), 0)  # 0.3 -> 0
        self.assertEqual(late_fee(1001, 4), 30)  # 30.03 -> 30


class Reject(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)
        with self.assertRaises(ValueError):
            late_fee(100, -1)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            late_fee(100, 366)

    def test_float(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)
        with self.assertRaises(ValueError):
            late_fee(100, 5.0)

    def test_str(self):
        with self.assertRaises(ValueError):
            late_fee("100", 5)

    def test_bool(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)
        with self.assertRaises(ValueError):
            late_fee(100, True)


if __name__ == "__main__":
    unittest.main()
