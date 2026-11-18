"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_normal_2(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_normal_3(self):
        self.assertEqual(late_fee(100000, 2), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # ช้า 3 วันพอดี ไม่คิด
        self.assertEqual(late_fee(100000, 3), 0)

    def test_boundary_2(self):   # 20 วัน = 15% พอดี
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_boundary_3(self):   # เกินเพดาน -> 15%
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 7.5 -> 8 (half-up)
        self.assertEqual(late_fee(200, 5), 8)

    def test_no_drift_2(self):   # 5.625 -> 6
        self.assertEqual(late_fee(150, 5), 6)

    def test_no_drift_3(self):   # 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)


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


if __name__ == "__main__":
    unittest.main()
