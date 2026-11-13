import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_3(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_normal_4(self):
        self.assertEqual(refund(20000, 25, True), 13125)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 79 -> คืน
        self.assertEqual(refund(10000, 79, False), 2100)

    def test_boundary_2(self):  # 80 พอดี ยังคืน
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_3(self):  # 81 ไม่คืน
        self.assertEqual(refund(10000, 81, False), 0)

    def test_boundary_4(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_boundary_5(self):
        self.assertEqual(refund(0, 0, True), 0)

    def test_boundary_6(self):
        self.assertEqual(refund(10000, 80, True), 1750)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 3.5 -> 4 (floor ได้ 3)
        self.assertEqual(refund(4, 0, True), 4)

    def test_no_drift_2(self):  # 1.5 -> 2
        self.assertEqual(refund(3, 50, False), 2)

    def test_no_drift_3(self):  # 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)

    def test_no_drift_4(self):  # 2.625 -> 3 ; ปัดสองรอบ (3 -> 2.625) จะต่าง
        self.assertEqual(refund(3, 0, True), 3)

    def test_no_drift_5(self):  # 0.4375 -> 0
        self.assertEqual(refund(1, 50, True), 0)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            refund(100, -1, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            refund(100, 101, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            refund(100.0, 0, False)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            refund('100', 0, False)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)

    def test_reject_7(self):
        with self.assertRaises(ValueError):
            refund(100, 50.0, False)

    def test_reject_8(self):
        with self.assertRaises(ValueError):
            refund(100, '50', False)

    def test_reject_9(self):
        with self.assertRaises(ValueError):
            refund(100, True, False)

    def test_reject_10(self):
        with self.assertRaises(ValueError):
            refund(100, 50, 1)

    def test_reject_11(self):
        with self.assertRaises(ValueError):
            refund(100, 50, None)

    def test_reject_12(self):
        with self.assertRaises(ValueError):
            refund(None, 50, False)


if __name__ == "__main__":
    unittest.main()
