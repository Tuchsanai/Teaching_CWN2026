"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(100000, 10), 7500)   # 7.5%

    def test_normal_2(self):
        self.assertEqual(late_fee(100000, 4), 3000)    # 3%

    def test_normal_3(self):
        self.assertEqual(late_fee(200000, 8), 12000)   # 6%


class Boundary(unittest.TestCase):
    def test_boundary_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_boundary_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)    # รวม 3 วันแรก

    def test_boundary_cap(self):
        self.assertEqual(late_fee(100000, 19), 14250)  # 14.25% ยังไม่ชนเพดาน
        self.assertEqual(late_fee(100000, 20), 15000)  # 15% พอดี
        self.assertEqual(late_fee(100000, 21), 15000)  # ชนเพดาน
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 365), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(late_fee(150, 4), 5)    # 4.5 -> 5 (half-up)

    def test_no_drift_2(self):
        self.assertEqual(late_fee(17, 5), 1)     # 0.6375 -> 1
        self.assertEqual(late_fee(10, 4), 0)     # 0.3 -> 0

    def test_no_drift_cap(self):
        self.assertEqual(late_fee(10, 365), 2)   # cap 1.5 -> 2
        self.assertEqual(late_fee(5, 365), 1)    # cap 0.75 -> 1


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)
        with self.assertRaises(ValueError):
            late_fee(100, -1)
        with self.assertRaises(ValueError):
            late_fee(100, 366)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            late_fee(1000.0, 5)
        with self.assertRaises(ValueError):
            late_fee(1000, 5.0)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            late_fee("1000", 5)
        with self.assertRaises(ValueError):
            late_fee(1000, "5")

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)
        with self.assertRaises(ValueError):
            late_fee(1000, True)
        with self.assertRaises(ValueError):
            late_fee(None, 5)


if __name__ == "__main__":
    unittest.main()
