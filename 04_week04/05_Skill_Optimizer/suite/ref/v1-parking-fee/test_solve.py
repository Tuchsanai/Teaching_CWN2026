"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import parking_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(parking_fee(45, False), 2675)

    def test_normal_2(self):
        self.assertEqual(parking_fee(120, False), 5350)

    def test_normal_3(self):
        self.assertEqual(parking_fee(60, True), 2274)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(parking_fee(30, False), 0)

    def test_boundary_2(self):
        self.assertEqual(parking_fee(31, False), 2675)

    def test_boundary_3(self):
        self.assertEqual(parking_fee(60, False), 2675)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(parking_fee(180, True), 6821)

    def test_no_drift_2(self):
        self.assertEqual(parking_fee(300, True), 11369)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            parking_fee(-1, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            parking_fee(1441, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            parking_fee(90.0, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            parking_fee('90', False)


if __name__ == "__main__":
    unittest.main()
