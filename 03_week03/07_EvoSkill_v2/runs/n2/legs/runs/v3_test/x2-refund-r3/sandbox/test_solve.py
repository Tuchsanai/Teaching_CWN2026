"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_3(self):
        self.assertEqual(refund(10000, 0, True), 8750)


class Boundary(unittest.TestCase):
    def test_boundary_80_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_81_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_boundary_100_and_zero_paid(self):
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(refund(9, 0, True), 7)  # 7.875 -> 7

    def test_no_drift_2(self):
        self.assertEqual(refund(3, 50, False), 1)  # 1.5 -> 1

    def test_no_drift_3(self):
        self.assertEqual(refund(101, 10, True), 79)  # 79.5375 -> 79


class Reject(unittest.TestCase):
    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_reject_percent_range(self):
        with self.assertRaises(ValueError):
            refund(100, 101, False)
        with self.assertRaises(ValueError):
            refund(100, -1, False)

    def test_reject_float_str(self):
        with self.assertRaises(ValueError):
            refund(100.0, 0, False)
        with self.assertRaises(ValueError):
            refund(100, "0", False)

    def test_reject_bool_and_restock(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)
        with self.assertRaises(ValueError):
            refund(100, 0, 1)


if __name__ == "__main__":
    unittest.main()
