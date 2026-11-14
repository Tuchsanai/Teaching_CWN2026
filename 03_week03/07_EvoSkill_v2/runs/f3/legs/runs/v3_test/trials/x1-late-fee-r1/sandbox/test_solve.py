"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_normal_2(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_normal_3(self):
        self.assertEqual(late_fee(100000, 3), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # ช้า 4 วัน = เริ่มคิด (4 x 0.75%)
        self.assertEqual(late_fee(10000, 4), 300)

    def test_boundary_2(self):   # 20 วัน = 15% พอดี
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_boundary_3(self):   # 365 วัน ติดเพดาน 15%
        self.assertEqual(late_fee(10000, 365), 1500)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 10 x 4 x 0.0075 = 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)

    def test_no_drift_2(self):   # 100 x 0.0075 x 5 = 3.75 -> 4 ; 200x4x.0075=6.0
        self.assertEqual(late_fee(100, 5), 4)

    def test_no_drift_3(self):   # 2 x 0.0075 x 4 = 0.06 -> 0 ; 1000x.0075x... half
        self.assertEqual(late_fee(200, 5), 8)  # 7.5 -> 8


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            late_fee("100", 5)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            late_fee(100, True)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            late_fee(100, 366)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            late_fee(100, -1)

    def test_reject_7(self):  # validate ก่อน แม้ช้าไม่เกิน 3 วัน
        with self.assertRaises(ValueError):
            late_fee(-5, 0)


if __name__ == "__main__":
    unittest.main()
