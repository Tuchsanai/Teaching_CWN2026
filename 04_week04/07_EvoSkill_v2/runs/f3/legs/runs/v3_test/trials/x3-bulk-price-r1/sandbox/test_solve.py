"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_2(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_3(self):
        self.assertEqual(bulk_price(10000, 10, True), 100674)  # 100673.625


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # 9 ถุง ไม่ลด
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_boundary_2(self):   # 49 ถุง ใช้ 3.5%
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_boundary_3(self):   # 50 ถุง ใช้ 7.5% อัตราเดียว
        self.assertEqual(bulk_price(10000, 50, False), 494875)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 1×0.965×1.07 = 1.03255 → 1
        self.assertEqual(bulk_price(1, 10, False), 10)

    def test_no_drift_2(self):   # 0.5 ปัดขึ้น: 50×1.07=53.5 → 54
        self.assertEqual(bulk_price(50, 1, False), 54)


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
            bulk_price(100, True, False)


if __name__ == "__main__":
    unittest.main()
