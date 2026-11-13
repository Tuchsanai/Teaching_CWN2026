import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_normal_2(self):
        self.assertEqual(late_fee(200000, 5), 7500)

    def test_normal_3(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_normal_4(self):
        self.assertEqual(late_fee(100000, 0), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 3 วัน ไม่คิด
        self.assertEqual(late_fee(100000, 3), 0)

    def test_boundary_2(self):  # 4 วัน คิดครบ 4 วัน
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_boundary_3(self):
        self.assertEqual(late_fee(100000, 2), 0)

    def test_boundary_4(self):  # ยังไม่ชนเพดาน
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_boundary_5(self):  # พอดีเพดาน
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_boundary_6(self):  # เกินเพดาน
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_boundary_7(self):
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)

    def test_no_drift_2(self):  # 2.625 -> 3
        self.assertEqual(late_fee(70, 5), 3)

    def test_no_drift_3(self):  # 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)

    def test_no_drift_4(self):  # 7.125 -> 7
        self.assertEqual(late_fee(50, 19), 7)

    def test_no_drift_5(self):  # เพดาน 7.5 -> 8
        self.assertEqual(late_fee(50, 20), 8)

    def test_no_drift_6(self):  # เพดาน 1.5 -> 2
        self.assertEqual(late_fee(10, 365), 2)

    def test_type_int(self):
        self.assertIs(type(late_fee(70, 5)), int)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            late_fee(1000, -1)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            late_fee(1000, 366)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            late_fee(1000.0, 5)

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            late_fee(1000, 5.0)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            late_fee('1000', 5)

    def test_reject_7(self):
        with self.assertRaises(ValueError):
            late_fee(1000, '5')

    def test_reject_8(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)

    def test_reject_9(self):
        with self.assertRaises(ValueError):
            late_fee(1000, True)

    def test_reject_10(self):
        with self.assertRaises(ValueError):
            late_fee(None, 5)

    def test_reject_11(self):
        with self.assertRaises(ValueError):
            late_fee(1000, None)


if __name__ == "__main__":
    unittest.main()
