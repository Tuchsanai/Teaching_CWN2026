"""รัน: python3 -m unittest -q test_solve  (ค่าที่คาดคำนวณมือ)"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(1000, 5, False), 5350)  # 5000*1.07

    def test_normal_2(self):
        self.assertEqual(bulk_price(1000, 10, True), 10067)  # 9408.75*1.07=10067.41

    def test_normal_3(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)  # 45093.75*1.07=48250.31


class Boundary(unittest.TestCase):
    def test_boundary_qty_10(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_boundary_qty_50(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5

    def test_boundary_range(self):
        self.assertEqual(bulk_price(0, 1, False), 0)
        self.assertEqual(bulk_price(100, 1, False), 107)
        self.assertEqual(bulk_price(1, 1000, False), 990)  # 989.75


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 half-up

    def test_no_drift_2(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 half-up

    def test_no_drift_3(self):
        self.assertEqual(bulk_price(1, 10, True), 10)  # 10.067


class Reject(unittest.TestCase):
    def test_reject_range(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            bulk_price(1000.0, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(1000, 1.0, False)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            bulk_price("1000", 1, False)

    def test_reject_bool_and_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(1000, True, False)
        for c in (1, 0, "yes", None):
            with self.assertRaises(ValueError):
                bulk_price(1000, 1, c)


if __name__ == "__main__":
    unittest.main()
