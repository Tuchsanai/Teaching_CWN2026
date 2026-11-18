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

    def test_over_5kg_proportional(self):
        self.assertEqual(shipping_fee(6000, 10, False), 9500)
        self.assertEqual(shipping_fee(5001, 10, False), 8002)  # 1.5 -> half up

    def test_distance_surcharge(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 10, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_pickup_and_express_limit(self):
        self.assertEqual(shipping_fee(500, 0, True), 0)
        self.assertEqual(shipping_fee(20000, 5, True), 45750)
        with self.assertRaises(ValueError):
            shipping_fee(20001, 5, True)

    def test_validation(self):
        for args in [(0, 1, False), (30001, 1, False), (1, -1, False),
                     (1.0, 1, False), (True, 1, False), (1, 1.5, False),
                     (1, 1, 1), (None, 1, False), ("5", 1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run('{"weight_g": 500, "distance_km": 10, "express": false}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4000})
        p = run('{"weight_g": 500}')
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        p = run("not json")
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
