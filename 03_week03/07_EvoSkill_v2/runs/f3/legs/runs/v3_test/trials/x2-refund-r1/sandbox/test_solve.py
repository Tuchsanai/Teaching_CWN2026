"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_normal_3(self):
        self.assertEqual(refund(20000, 0, False), 20000)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # 80% พอดียังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_2(self):   # 81% ไม่คืน
        self.assertEqual(refund(10000, 81, False), 0)

    def test_boundary_3(self):   # paid 0
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 875.875 -> floor 875
        self.assertEqual(refund(1001, 0, True), 875)

    def test_no_drift_2(self):   # 33.33.. -> 33
        self.assertEqual(refund(99, 67, False), 32)  # 99*33/100=32.67 -> 32


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            refund(-1, 10, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            refund(100.0, 10, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            refund("100", 10, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            refund(100, 10, 1)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            refund(100, 101, False)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            refund(100, True, False)


if __name__ == "__main__":
    unittest.main()
