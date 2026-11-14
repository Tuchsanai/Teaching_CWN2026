import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_light(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_heavy(self):
        self.assertEqual(shipping_fee(6000, 10, False), 9500)

    def test_far_express(self):
        self.assertEqual(shipping_fee(6000, 101, True), 17100)


class Boundary(unittest.TestCase):
    def test_1000_1001(self):
        self.assertEqual(shipping_fee(1000, 1, False), 4000)
        self.assertEqual(shipping_fee(1001, 1, False), 8000)

    def test_5000(self):
        self.assertEqual(shipping_fee(5000, 1, False), 8000)

    def test_distance_100_101(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_pickup_zero(self):
        self.assertEqual(shipping_fee(500, 0, True), 0)

    def test_express_cap(self):
        self.assertEqual(shipping_fee(20000, 1, True), 45750)


class NoDrift(unittest.TestCase):
    def test_half_satang(self):
        self.assertEqual(shipping_fee(5001, 1, False), 8002)  # 8001.5

    def test_far(self):
        self.assertEqual(shipping_fee(5001, 101, False), 9602)  # 9601.8


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10.0, False)
        with self.assertRaises(ValueError):
            shipping_fee(500.0, 10, False)

    def test_str_none_bool(self):
        for a in [("5", 1, False), (None, 1, False), (True, 1, False), (500, True, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_range(self):
        for a in [(0, 1, False), (30001, 1, False), (500, -1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_flag(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 1, 1)

    def test_express_heavy(self):
        with self.assertRaises(ValueError):
            shipping_fee(20001, 1, True)
        with self.assertRaises(ValueError):
            shipping_fee(20001, 0, True)


if __name__ == "__main__":
    unittest.main()
