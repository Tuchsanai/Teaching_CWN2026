import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, True), 4375)  # 5000*7/8

    def test_normal_3(self):
        self.assertEqual(refund(10000, 0, True), 8750)


class Boundary(unittest.TestCase):
    def test_boundary_80_still_refunds(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 80, True), 175)

    def test_boundary_81_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_boundary_extremes(self):
        self.assertEqual(refund(1000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(1000, 0, False), 1000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(refund(995, 50, False), 497)  # 497.5 ปัดลง

    def test_no_drift_2(self):
        self.assertEqual(refund(1001, 0, True), 875)  # 875.875 ปัดลง

    def test_no_drift_3(self):
        self.assertEqual(refund(999, 33, False), 669)  # 669.33


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
            refund(100.0, 10, False)
        with self.assertRaises(ValueError):
            refund("100", 10, False)
        with self.assertRaises(ValueError):
            refund(100, 10.0, False)

    def test_reject_bool_and_restock(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)
        with self.assertRaises(ValueError):
            refund(100, 10, 1)
        with self.assertRaises(ValueError):
            refund(100, 10, "yes")


if __name__ == "__main__":
    unittest.main()
