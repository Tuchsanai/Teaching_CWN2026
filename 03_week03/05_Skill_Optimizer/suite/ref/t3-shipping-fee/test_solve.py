"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(shipping_fee(500, 20, False), 4000)

    def test_normal_2(self):
        self.assertEqual(shipping_fee(3000, 20, False), 8000)

    def test_normal_3(self):
        self.assertEqual(shipping_fee(3000, 150, False), 9600)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(shipping_fee(1000, 10, False), 4000)

    def test_boundary_2(self):
        self.assertEqual(shipping_fee(1001, 10, False), 8000)

    def test_boundary_3(self):
        self.assertEqual(shipping_fee(5000, 10, False), 8000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(shipping_fee(5106, 150, True), 14686)

    def test_no_drift_2(self):
        self.assertEqual(shipping_fee(5217, 50, True), 12488)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            shipping_fee(-5, 10, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000.0, 10, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            shipping_fee('1000', 10, False)


if __name__ == "__main__":
    unittest.main()
