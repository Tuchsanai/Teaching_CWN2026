import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):  # 10000 * 0.75% * 10 = 750
        self.assertEqual(late_fee(10000, 10), 750)

    def test_normal_2(self):  # 20000 * 0.75% * 5 = 750
        self.assertEqual(late_fee(20000, 5), 750)

    def test_normal_3(self):
        self.assertEqual(late_fee(100000, 7), 5250)

    def test_normal_4(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # ช้า 0 และ 3 วัน ไม่คิด
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_boundary_2(self):  # 4 วัน นับรวม 3 วันแรก = 3% 
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_boundary_3(self):  # 19 วัน ยังไม่ชนเพดาน = 14.25%
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_boundary_4(self):  # 20 วัน พอดีเพดาน 15%
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_boundary_5(self):  # 21 วัน และ 365 วัน เกินเพดาน
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 150*0.03 = 4.5 -> 5 (floor/banker's ได้ 4)
        self.assertEqual(late_fee(150, 4), 5)

    def test_no_drift_2(self):  # 100*0.03 = 3.0 ; 149*0.03=4.47 -> 4
        self.assertEqual(late_fee(100, 4), 3)
        self.assertEqual(late_fee(149, 4), 4)

    def test_no_drift_3(self):  # 151*0.03=4.53 -> 5
        self.assertEqual(late_fee(151, 4), 5)

    def test_no_drift_4(self):  # เพดาน 10*0.15=1.5 -> 2 ; 10*0.0075*10=0.75->1
        self.assertEqual(late_fee(10, 30), 2)
        self.assertEqual(late_fee(10, 10), 1)


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
            late_fee(1000, False)

    def test_reject_10(self):
        with self.assertRaises(ValueError):
            late_fee(None, 5)

    def test_reject_11(self):
        with self.assertRaises(ValueError):
            late_fee(1000, None)


if __name__ == "__main__":
    unittest.main()
