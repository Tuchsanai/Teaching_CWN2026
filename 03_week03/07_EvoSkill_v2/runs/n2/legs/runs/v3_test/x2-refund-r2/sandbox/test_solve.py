"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, True), 4375)  # 5000*7/8

    def test_normal_3(self):
        self.assertEqual(refund(2000, 20, False), 1600)


class Boundary(unittest.TestCase):
    def test_boundary_80_refunds(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 80, True), 175)

    def test_boundary_81_none(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_boundary_0_and_100(self):
        self.assertEqual(refund(800, 0, False), 800)
        self.assertEqual(refund(800, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(refund(999, 0, True), 874)  # 874.125

    def test_no_drift_2(self):
        self.assertEqual(refund(1001, 33, False), 670)  # 670.67 ปัดลง

    def test_no_drift_3(self):
        self.assertEqual(refund(1001, 33, True), 586)  # 586.836 ปัดลง


class Reject(unittest.TestCase):
    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            refund(-1, 10, False)

    def test_reject_percent_range(self):
        with self.assertRaises(ValueError):
            refund(100, 101, False)
        with self.assertRaises(ValueError):
            refund(100, -1, False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            refund(100.0, 10, False)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            refund(100, "10", False)

    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)
        with self.assertRaises(ValueError):
            refund(100, 10, 1)


if __name__ == "__main__":
    unittest.main()
