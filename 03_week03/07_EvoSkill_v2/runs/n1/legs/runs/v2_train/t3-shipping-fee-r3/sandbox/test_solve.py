import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_normal_2(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_normal_3(self):
        # 8000 + 5000*1.5 = 15500
        self.assertEqual(f(10000, 50, False), 15500)

    def test_normal_4(self):
        # 4000*1.2*1.5 = 7200
        self.assertEqual(f(1000, 200, True), 7200)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)

    def test_boundary_2(self):
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)

    def test_boundary_3(self):
        # 8000 + 1*1.5 = 8001.5 -> 8002
        self.assertEqual(f(5001, 0, False), 8002)

    def test_boundary_4(self):
        # 8000 + 25000*1.5 = 45500
        self.assertEqual(f(30000, 0, False), 45500)

    def test_boundary_5(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1000, 101, False), 4800)
        self.assertEqual(f(1000, 99, False), 4000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        # 8001.5 -> 8002 (floor ได้ 8001)
        self.assertEqual(f(5001, 0, False), 8002)

    def test_no_drift_2(self):
        # 8001.5*1.2 = 9601.8 -> 9602
        self.assertEqual(f(5001, 101, False), 9602)

    def test_no_drift_3(self):
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)

    def test_no_drift_4(self):
        # 8001.5*1.8 = 14402.7 -> 14403 (ปัดสองรอบจะได้ 9602*1.5=14403 เท่ากัน)
        self.assertEqual(f(5001, 101, True), 14403)

    def test_no_drift_5(self):
        # 8003*1.5 = 12004.5 -> 12005 (half-up; round() ได้ 12004)
        self.assertEqual(f(5002, 0, True), 12005)

    def test_no_drift_6(self):
        # (8000+1.5*3)=8004.5 -> 8005 ; ยืนยัน .5 ปัดขึ้น
        self.assertEqual(f(5003, 0, False), 8005)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            f(*a)

    def test_reject_1(self):
        self.bad(0, 10, False)

    def test_reject_2(self):
        self.bad(30001, 10, False)

    def test_reject_3(self):
        self.bad(-5, 10, False)

    def test_reject_4(self):
        self.bad(500, -1, False)

    def test_reject_5(self):
        self.bad(500.0, 10, False)

    def test_reject_6(self):
        self.bad('500', 10, False)

    def test_reject_7(self):
        self.bad(True, 10, False)

    def test_reject_8(self):
        self.bad(None, 10, False)

    def test_reject_9(self):
        self.bad(500, 10.0, False)

    def test_reject_10(self):
        self.bad(500, '10', False)

    def test_reject_11(self):
        self.bad(500, None, False)

    def test_reject_12(self):
        self.bad(500, 10, 1)

    def test_reject_13(self):
        self.bad(500, 10, None)

    def test_reject_14(self):
        self.bad(500, 10, 'true')


if __name__ == "__main__":
    unittest.main()
