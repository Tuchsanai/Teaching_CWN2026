import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_normal_2(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_normal_3(self):
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_normal_4(self):
        self.assertEqual(split_bill(12345, 4, 12), [3457, 3457, 3456, 3456])


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_boundary_2(self):
        self.assertEqual(split_bill(999, 1, 0), [999])

    def test_boundary_3(self):  # tip 100
        self.assertEqual(split_bill(101, 3, 100), [68, 67, 67])

    def test_boundary_4(self):  # คนมากกว่าสตางค์
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_boundary_5(self):  # หารลงตัวพอดี ไม่มีเศษ
        self.assertEqual(split_bill(300, 3, 0), [100, 100, 100])

    def test_boundary_6(self):  # tip 1
        self.assertEqual(split_bill(10000, 1, 1), [10100])


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 5.5 -> 6 (floor ได้ 5)
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_no_drift_2(self):  # 16.5 -> 17 (round() ได้ 16)
        self.assertEqual(split_bill(15, 1, 10), [17])

    def test_no_drift_3(self):  # 15.4 -> 15
        self.assertEqual(split_bill(14, 1, 10), [15])

    def test_no_drift_4(self):  # 17.6 -> 18 แล้วหาร 2
        self.assertEqual(split_bill(16, 2, 10), [9, 9])

    def test_no_drift_5(self):  # รวมก่อนปัดครั้งเดียว: 3*105/100 = 3.15 -> 3
        self.assertEqual(split_bill(3, 2, 5), [2, 1])


class Reject(unittest.TestCase):
    def check(self, *a):
        with self.assertRaises(ValueError):
            split_bill(*a)

    def test_reject_total(self):
        for v in (-1, 1.0, '100', True, None):
            self.check(v, 2, 0)

    def test_reject_people(self):
        for v in (0, -1, 2.0, '2', True, None):
            self.check(100, v, 0)

    def test_reject_tip(self):
        for v in (-1, 101, 10.0, '10', True, None):
            self.check(100, 2, v)


if __name__ == "__main__":
    unittest.main()
