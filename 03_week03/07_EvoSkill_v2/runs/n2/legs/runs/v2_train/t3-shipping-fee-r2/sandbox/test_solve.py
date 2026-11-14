import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_normal_2(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)

    def test_normal_3(self):
        # 80 + 5*15 = 155 บาท; *1.2 = 186; *1.5 = 279 บาท
        self.assertEqual(shipping_fee(10000, 150, True), 27900)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1001, 100, False), 8000)

    def test_boundary_2(self):
        self.assertEqual(shipping_fee(5000, 101, False), 9600)
        self.assertEqual(shipping_fee(5001, 100, False), 8000 + 2)  # 1.5 สตางค์ -> 8001.5 -> 8002

    def test_boundary_3(self):
        self.assertEqual(shipping_fee(1, 0, False), 0)
        # 80 + 15*15 = 305 บาท; *1.5 = 457.50 บาท
        self.assertEqual(shipping_fee(20000, 1, True), 45750)
        with self.assertRaises(ValueError):
            shipping_fee(20001, 1, True)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        # 8001.5 สตางค์ -> ปัดขึ้น 8002
        self.assertEqual(shipping_fee(5001, 1, False), 8002)

    def test_no_drift_2(self):
        # 8000 + 1.5*3 = 8004.5; *1.2 = 9605.4; *1.5 = 14408.1 -> 14408
        self.assertEqual(shipping_fee(5003, 101, True), 14408)


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
        for args in [(True, 1, False), (1000, 1, 1), (1000, True, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)


if __name__ == "__main__":
    unittest.main()
