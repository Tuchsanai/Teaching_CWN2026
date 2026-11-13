import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_normal_2(self):
        self.assertEqual(late_fee(200000, 10), 15000)

    def test_normal_3(self):
        self.assertEqual(late_fee(10000, 19), 1425)

    def test_normal_4(self):
        self.assertEqual(late_fee(0, 30), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # ไม่เกิน 3 วัน
        self.assertEqual(late_fee(10000, 3), 0)

    def test_boundary_2(self):  # วันที่ 4 คิดย้อนหลังรวม 3 วันแรก
        self.assertEqual(late_fee(10000, 4), 300)

    def test_boundary_3(self):
        self.assertEqual(late_fee(10000, 5), 375)

    def test_boundary_4(self):
        self.assertEqual(late_fee(10000, 0), 0)

    def test_boundary_5(self):  # ยังไม่ชนเพดาน
        self.assertEqual(late_fee(10000, 19), 1425)

    def test_boundary_6(self):  # พอดีเพดาน 15%
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_boundary_7(self):  # เกินเพดาน
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)

    def test_no_drift_2(self):  # 4.5 -> 5
        self.assertEqual(late_fee(100, 6), 5)

    def test_no_drift_3(self):  # 2.1 -> 2
        self.assertEqual(late_fee(70, 4), 2)

    def test_no_drift_4(self):  # 3.375 -> 3
        self.assertEqual(late_fee(90, 5), 3)

    def test_no_drift_5(self):  # เพดาน 1.5 -> 2
        self.assertEqual(late_fee(10, 365), 2)


class Reject(unittest.TestCase):
    def check(self, *args):
        with self.assertRaises(ValueError):
            late_fee(*args)

    def test_reject_1(self):
        self.check(-1, 5)

    def test_reject_2(self):
        self.check(1000, -1)

    def test_reject_3(self):
        self.check(1000, 366)

    def test_reject_4(self):
        self.check(1000.0, 5)

    def test_reject_5(self):
        self.check(1000, 5.0)

    def test_reject_6(self):
        self.check('1000', 5)

    def test_reject_7(self):
        self.check(1000, '5')

    def test_reject_8(self):
        self.check(True, 5)

    def test_reject_9(self):
        self.check(1000, True)

    def test_reject_10(self):
        self.check(None, 5)

    def test_reject_11(self):
        self.check(1000, None)


if __name__ == "__main__":
    unittest.main()
