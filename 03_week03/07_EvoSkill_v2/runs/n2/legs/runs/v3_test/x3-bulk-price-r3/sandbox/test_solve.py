"""รัน: python3 -m unittest -q test_solve (ค่าที่คาดคำนวณมือ)"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)

    def test_normal_2(self):
        # 50000*.925*.975*1.07 = 48250.3125
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_normal_3(self):
        self.assertEqual(bulk_price(0, 5, True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_boundary_2(self):
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5

    def test_boundary_3(self):
        self.assertEqual(bulk_price(1000, 1, True), 1043)  # 1043.25
        self.assertEqual(bulk_price(1, 1000, False), 990)  # 1000*.925*1.07=989.75


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> up

    def test_no_drift_2(self):
        self.assertEqual(bulk_price(999, 1, True), 1042)  # 1042.15


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1.0, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            bulk_price("100", 1, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, None)


if __name__ == "__main__":
    unittest.main()
