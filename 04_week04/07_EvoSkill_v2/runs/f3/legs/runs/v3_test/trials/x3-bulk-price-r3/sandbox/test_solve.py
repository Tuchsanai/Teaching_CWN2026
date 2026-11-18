"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)

    def test_normal_2(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_normal_3(self):
        self.assertEqual(bulk_price(1234, 10, True), 12423)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # 9 ถุง ไม่ลด
        self.assertEqual(bulk_price(1000, 9, False), 9630)

    def test_boundary_2(self):   # 10 ถุง ลด 3.5%
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_boundary_3(self):   # 49 vs 50
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        
    def test_boundary_4(self):   # 50 ถุง ลด 7.5%
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_boundary_5(self):   # ราคา 0 / qty สูงสุด
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundary_6(self):
        self.assertEqual(bulk_price(333, 1000, True), 321347)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 10325.5 -> half-up
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_no_drift_2(self):   # 1.07 -> 1
        self.assertEqual(bulk_price(1, 1, False), 1)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            bulk_price("100", 1, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_reject_7(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)


if __name__ == "__main__":
    unittest.main()
