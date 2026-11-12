import unittest
from solve import shipping_fee, main


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 25 * 1500)

    def test_fraction_rounding(self):
        # 5001 g -> 8000 + 1.5 = 8001.5 -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)
        self.assertEqual(shipping_fee(5002, 0, False), 8003)

    def test_distance_express(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 100.5, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)
        # 5001g, far, express: 8001.5*1.2*1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (1.5, 1, False), (True, 1, False),
                     ("5", 1, False), (1, -1, False), (1, "x", False),
                     (1, float("nan"), False), (1, 1, 1), (1, 1, None)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        self.assertEqual(main(['{"weight_g":500,"distance_km":0,"express":true}']), 0)
        self.assertEqual(main(['{"weight_g":0,"distance_km":0,"express":true}']), 1)
        self.assertEqual(main(['not json']), 1)
        self.assertEqual(main(['{"weight_g":5}']), 1)


if __name__ == "__main__":
    unittest.main()
