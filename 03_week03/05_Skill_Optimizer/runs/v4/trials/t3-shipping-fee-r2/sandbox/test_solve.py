import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 10, False), 4000)
        self.assertEqual(shipping_fee(1001, 10, False), 8000)
        self.assertEqual(shipping_fee(5000, 10, False), 8000)

    def test_over_5000_prorated(self):
        self.assertEqual(shipping_fee(5001, 10, False), 8002)  # 1.5 -> 2 half up
        self.assertEqual(shipping_fee(6000, 10, False), 9500)

    def test_distance_surcharge(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 10, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)
        self.assertEqual(shipping_fee(20000, 10, True), 15 * 0 + (8000 + 22500) * 3 // 2)

    def test_zero_distance_free(self):
        self.assertEqual(shipping_fee(500, 0, True), 0)

    def test_express_limit(self):
        with self.assertRaises(ValueError):
            shipping_fee(20001, 10, True)
        self.assertEqual(shipping_fee(30000, 10, False), 8000 + 25000 * 150 // 100)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (1.5, 1, False),
                     (True, 1, False), (10, -1, False), (10, 1.0, False),
                     (10, 1, 1)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"weight_g": 500, "distance_km": 10, "express": True}))
        self.assertEqual(json.loads(r.stdout), {"fee_satang": 6000})


if __name__ == "__main__":
    unittest.main()
