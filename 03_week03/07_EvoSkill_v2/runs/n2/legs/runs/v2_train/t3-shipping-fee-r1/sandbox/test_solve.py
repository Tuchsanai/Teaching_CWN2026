import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_normal_2(self):
        self.assertEqual(shipping_fee(3000, 150, False), 9600)  # 80*1.2

    def test_normal_3(self):
        self.assertEqual(shipping_fee(10000, 50, True), 23250)  # (80+75)*1.5


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(shipping_fee(1000, 1, False), 4000)
        self.assertEqual(shipping_fee(1001, 1, False), 8000)

    def test_boundary_2(self):
        self.assertEqual(shipping_fee(5000, 100, False), 8000)
        self.assertEqual(shipping_fee(5001, 101, False), 9602)  # 8001.5*1.2=9601.8

    def test_boundary_3(self):
        self.assertEqual(shipping_fee(1, 0, False), 0)
        self.assertEqual(shipping_fee(20000, 5, True), 45750)  # (80+225)*1.5=457.5 baht


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        # 5001 g: 80.015 baht = 8001.5 -> 8002
        self.assertEqual(shipping_fee(5001, 1, False), 8002)

    def test_no_drift_2(self):
        # 5001,101km,express: 8001.5*1.2*1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for args in [(0, 1, False), (30001, 1, False), (1, -1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000.0, 1, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            shipping_fee("1000", 1, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 1, False)
        with self.assertRaises(ValueError):
            shipping_fee(100, 1, 1)

    def test_reject_express_over_20000(self):
        with self.assertRaises(ValueError):
            shipping_fee(20001, 0, True)


if __name__ == "__main__":
    unittest.main()
