import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_normal_2(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_normal_3(self):
        self.assertEqual(refund(20000, 25, True), 13125)

    def test_normal_4(self):
        self.assertEqual(refund(0, 0, True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 80% ยังคืน
        self.assertEqual(refund(1000, 80, False), 200)

    def test_boundary_2(self):
        self.assertEqual(refund(1000, 80, True), 175)

    def test_boundary_3(self):  # 81% ไม่คืน
        self.assertEqual(refund(1000, 81, False), 0)

    def test_boundary_4(self):
        self.assertEqual(refund(1000, 79, False), 210)

    def test_boundary_5(self):
        self.assertEqual(refund(1000, 100, True), 0)

    def test_boundary_6(self):
        self.assertEqual(refund(1000, 0, False), 1000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)

    def test_no_drift_2(self):  # 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_no_drift_3(self):  # 9.5 -> 10
        self.assertEqual(refund(10, 5, False), 10)

    def test_no_drift_4(self):  # 2.1875 -> 2 (ปัดสองรอบจะได้ 3)
        self.assertEqual(refund(5, 50, True), 2)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            refund(*a)

    def test_reject_1(self):
        self.bad(-1, 10, False)

    def test_reject_2(self):
        self.bad(1000, -1, False)

    def test_reject_3(self):
        self.bad(1000, 101, False)

    def test_reject_4(self):
        self.bad(1000.0, 10, False)

    def test_reject_5(self):
        self.bad('1000', 10, False)

    def test_reject_6(self):
        self.bad(True, 10, False)

    def test_reject_7(self):
        self.bad(1000, 10.0, False)

    def test_reject_8(self):
        self.bad(1000, '10', False)

    def test_reject_9(self):
        self.bad(1000, True, False)

    def test_reject_10(self):
        self.bad(1000, 10, 1)

    def test_reject_11(self):
        self.bad(1000, 10, None)

    def test_reject_12(self):
        self.bad(None, 10, False)


if __name__ == "__main__":
    unittest.main()
