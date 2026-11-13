import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_normal_2(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)

    def test_normal_3(self):
        self.assertEqual(shipping_fee(10000, 50, False), 15500)

    def test_normal_4(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    def test_boundary_2(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_boundary_3(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_boundary_4(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_boundary_5(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_boundary_6(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)

    def test_boundary_7(self):
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_boundary_8(self):
        self.assertEqual(shipping_fee(500, 99, False), 4000)

    def test_boundary_9(self):
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_boundary_10(self):
        self.assertEqual(shipping_fee(30000, 101, True), 81900)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 8004.5 -> 8005 (round() ได้ 8004)
        self.assertEqual(shipping_fee(5003, 0, False), 8005)

    def test_no_drift_2(self):  # 8001.5*1.2 = 9601.8 -> 9602
        self.assertEqual(shipping_fee(5001, 101, False), 9602)

    def test_no_drift_3(self):  # 8001.5*1.5 = 12002.25 -> 12002 (ปัดกลางทางจะได้ 12003)
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    def test_no_drift_4(self):  # 8001.5*1.8 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_no_drift_5(self):  # 8004.5*1.5 = 12006.75 -> 12007
        self.assertEqual(shipping_fee(5003, 0, True), 12007)


class Reject(unittest.TestCase):
    def check(self, *args):
        with self.assertRaises(ValueError):
            shipping_fee(*args)

    def test_reject_1(self):
        self.check(0, 10, False)

    def test_reject_2(self):
        self.check(-5, 10, False)

    def test_reject_3(self):
        self.check(30001, 10, False)

    def test_reject_4(self):
        self.check(500, -1, False)

    def test_reject_5(self):
        self.check(500.0, 10, False)

    def test_reject_6(self):
        self.check('500', 10, False)

    def test_reject_7(self):
        self.check(True, 10, False)

    def test_reject_8(self):
        self.check(None, 10, False)

    def test_reject_9(self):
        self.check(500, 10.0, False)

    def test_reject_10(self):
        self.check(500, '10', False)

    def test_reject_11(self):
        self.check(500, True, False)

    def test_reject_12(self):
        self.check(500, None, False)

    def test_reject_13(self):
        self.check(500, 10, 1)

    def test_reject_14(self):
        self.check(500, 10, 'true')

    def test_reject_15(self):
        self.check(500, 10, None)


if __name__ == "__main__":
    unittest.main()
