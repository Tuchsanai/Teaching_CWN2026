import unittest
from solve import shipping_fee


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_excess(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 -> half-up 2
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_single_rounding(self):
        # 8001.5 *1.2*1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (1, -1, False), (1.5, 0, False),
                  (True, 0, False), (1, 0, 1), ("1", 0, False), (1, 0.5, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_returns_int(self):
        self.assertIs(type(shipping_fee(7777, 150, True)), int)


if __name__ == "__main__":
    unittest.main()
