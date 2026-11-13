import unittest
from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)
        self.assertEqual(shipping_fee(3000, 10, False), 8000)
        self.assertEqual(shipping_fee(10000, 10, False), 15500)  # 80+5*15=155 บาท
        self.assertEqual(shipping_fee(500, 150, True), 7200)     # 40*1.2*1.5=72
        self.assertEqual(shipping_fee(10000, 101, True), 27900)  # 155*1.8=279


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 80.015 บาท -> 8001.5 -> 8002
        self.assertEqual(shipping_fee(30000, 0, False), 45500)
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 8001.5 * 1.5 = 12002.25 -> 12002 ; 5003 g: 8004.5 -> *1.5=12006.75
        self.assertEqual(shipping_fee(5001, 0, True), 12002)
        self.assertEqual(shipping_fee(5003, 0, True), 12007)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # .5 ปัดขึ้น
        self.assertIsInstance(shipping_fee(5001, 150, True), int)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(0, 1, False), (30001, 1, False), (-5, 1, False), (500.0, 1, False),
                     ("500", 1, False), (True, 1, False), (None, 1, False),
                     (500, -1, False), (500, "5", False), (500, None, False),
                     (500, True, False), (500, 1, 1), (500, 1, "yes"), (500, 1, None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                shipping_fee(*args)


if __name__ == "__main__":
    unittest.main()
