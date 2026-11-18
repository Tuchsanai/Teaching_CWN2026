import unittest
from solve import shipping_fee


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 10, False), 4000)
        self.assertEqual(shipping_fee(1001, 10, False), 8000)
        self.assertEqual(shipping_fee(5000, 10, False), 8000)

    def test_over_5000(self):
        self.assertEqual(shipping_fee(6000, 10, False), 9500)
        self.assertEqual(shipping_fee(5001, 10, False), 8002)  # 1.5 -> 2

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 10, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_zero_km_and_express_limit(self):
        self.assertEqual(shipping_fee(30000, 0, True), 0)
        self.assertEqual(shipping_fee(20000, 5, True), (8000 + 22500) * 3 // 2)
        with self.assertRaises(ValueError):
            shipping_fee(20001, 5, True)

    def test_invalid(self):
        for a in [(0, 1, False), (30001, 1, False), (1.5, 1, False),
                  (True, 1, False), (100, -1, False), (100, 1.0, False),
                  (100, 1, 1)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)


if __name__ == "__main__":
    unittest.main()
