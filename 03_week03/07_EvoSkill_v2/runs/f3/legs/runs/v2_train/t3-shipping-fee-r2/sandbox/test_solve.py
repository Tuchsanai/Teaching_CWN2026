import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_light(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_far(self):
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 10, True), 6000)

    def test_far_express(self):
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_heavy(self):
        self.assertEqual(shipping_fee(30000, 10, False), 45500)


class Boundary(unittest.TestCase):
    def test_1000(self):
        self.assertEqual(shipping_fee(1000, 10, False), 4000)

    def test_1001(self):
        self.assertEqual(shipping_fee(1001, 10, False), 8000)

    def test_5000(self):
        self.assertEqual(shipping_fee(5000, 10, False), 8000)

    def test_5001(self):
        self.assertEqual(shipping_fee(5001, 10, False), 8002)

    def test_distance_100_vs_101(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express_cap(self):
        self.assertEqual(shipping_fee(20000, 10, True), 45750)
        with self.assertRaises(ValueError):
            shipping_fee(20001, 10, True)

    def test_pickup(self):
        self.assertEqual(shipping_fee(500, 0, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_satang_up(self):
        self.assertEqual(shipping_fee(5003, 10, False), 8005)  # 8004.5

    def test_far_fraction(self):
        self.assertEqual(shipping_fee(5001, 101, False), 9602)  # 9601.8

    def test_express_fraction(self):
        self.assertEqual(shipping_fee(5001, 10, True), 12002)  # 12002.25


class Reject(unittest.TestCase):
    def test_float(self):
        for a in [(500.0, 10, False), (500, 10.5, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_str_none_bool(self):
        for a in [("500", 10, False), (None, 10, False), (True, 10, False), (500, True, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_range(self):
        for a in [(0, 10, False), (30001, 10, False), (500, -1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_flag(self):
        for a in [(500, 10, 1), (500, 10, "yes"), (500, 10, None)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_validate_before_pickup(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 0, False)


if __name__ == "__main__":
    unittest.main()
