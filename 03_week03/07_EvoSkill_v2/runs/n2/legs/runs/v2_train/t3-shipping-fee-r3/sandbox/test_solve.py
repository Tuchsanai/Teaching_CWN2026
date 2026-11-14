"""รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_normal_2(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)

    def test_normal_3(self):
        # 8000+5*1500=15500 ; *1.2=18600 ; *1.5=27900
        self.assertEqual(shipping_fee(10000, 150, True), 27900)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1001, 100, False), 8000)

    def test_boundary_2(self):
        self.assertEqual(shipping_fee(5000, 101, False), 9600)
        self.assertEqual(shipping_fee(5001, 100, False), 8002)  # 8001.5 -> half-up

    def test_boundary_3(self):
        self.assertEqual(shipping_fee(20000, 1, True), 45750)  # (8000+22500)*1.5
        with self.assertRaises(ValueError):
            shipping_fee(20001, 1, True)
        self.assertEqual(shipping_fee(30000, 1, False), 8000 + 37500)
        self.assertEqual(shipping_fee(1, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(shipping_fee(5001, 100, False), 8002)

    def test_no_drift_2(self):
        # 8001.5*1.2=9601.8 -> 9602
        self.assertEqual(shipping_fee(5001, 101, False), 9602)

    def test_no_drift_3(self):
        # 8001.5*1.5=12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 100, True), 12002)


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
        for args in [(True, 1, False), (1, 1, 1), (1, True, False), (1, 1, "yes")]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)


if __name__ == "__main__":
    unittest.main()
