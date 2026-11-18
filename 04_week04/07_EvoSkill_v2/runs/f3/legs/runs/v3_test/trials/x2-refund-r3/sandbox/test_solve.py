"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_3(self):
        self.assertEqual(refund(10000, 50, True), 4375)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # 80% ยังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_2(self):   # 81% ไม่คืน
        self.assertEqual(refund(10000, 81, False), 0)

    def test_boundary_3(self):
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 33*0.875=28.875 -> floor 28
        self.assertEqual(refund(33, 0, True), 28)

    def test_no_drift_2(self):   # 999*0.7=699.3 -> 699
        self.assertEqual(refund(999, 30, False), 699)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            refund(100.0, 0, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            refund(100, 101, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            refund(100, 10, 1)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            refund("100", 10, False)

    def test_reject_6(self):   # validate ก่อนคืน 0
        with self.assertRaises(ValueError):
            refund(100, 90.5, False)


if __name__ == "__main__":
    unittest.main()
