import unittest
from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_excess_weight(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 -> 2
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_returns_int(self):
        self.assertIs(type(shipping_fee(5003, 150, True)), int)

    def test_invalid_weight(self):
        for w in (0, 30001, -1, 1.5, True, "5", None):
            with self.assertRaises(ValueError):
                shipping_fee(w, 0, False)

    def test_invalid_distance_express(self):
        for d in (-1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                shipping_fee(100, d, False)
        for e in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                shipping_fee(100, 0, e)


if __name__ == "__main__":
    unittest.main()
