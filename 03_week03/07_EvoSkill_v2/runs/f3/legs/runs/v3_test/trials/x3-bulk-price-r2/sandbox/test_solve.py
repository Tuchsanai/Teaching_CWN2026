"""เทสต์ของ solve.py: python3 -m unittest -q test_solve"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_normal_2(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_3(self):
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # 49 ถุง ยังได้ 3.5%
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_boundary_2(self):   # ราคา 0
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundary_3(self):   # qty สูงสุด 1000: 1000*0.925*1.07
        self.assertEqual(bulk_price(100, 1000, False), 98975)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):   # 50*1*1.07 = 53.5 -> 54
        self.assertEqual(bulk_price(50, 1, False), 54)

    def test_no_drift_2(self):   # 40*50*0.925*1.07 = 1979.5 -> 1980
        self.assertEqual(bulk_price(40, 50, False), 1980)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            bulk_price(100, "3", False)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)

    def test_reject_7(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)


if __name__ == "__main__":
    unittest.main()
