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

    def test_over_5kg(self):
        self.assertEqual(shipping_fee(6000, 10, False), 9500)
        self.assertEqual(shipping_fee(5001, 10, False), 8002)  # 8001.5 ปัดขึ้น

    def test_distance_surcharge(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 10, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_pickup_free(self):
        self.assertEqual(shipping_fee(500, 0, False), 0)
        self.assertEqual(shipping_fee(500, 0, True), 0)

    def test_invalid(self):
        for args in [(0, 5, False), (30001, 5, False), (500, -1, False),
                     (500.0, 5, False), (True, 5, False), (500, 5.0, False),
                     (500, 5, 1), (20001, 5, True), ("5", 5, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_express_limit_ok(self):
        self.assertEqual(shipping_fee(20000, 10, True), int((8000 + 22500) * 1.5))

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"weight_g": 500, "distance_km": 10, "express": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4000})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="{bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
