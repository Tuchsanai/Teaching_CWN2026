import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tier_1(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_tier_2(self):
        self.assertEqual(shipping_fee(1001, 10, False), 8000)
        self.assertEqual(shipping_fee(5000, 10, False), 8000)

    def test_over_5000(self):
        self.assertEqual(shipping_fee(6000, 10, False), 9500)
        self.assertEqual(shipping_fee(30000, 10, False), 45500)

    def test_half_up_once(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_distance_and_express(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)
        self.assertEqual(shipping_fee(6000, 0, True), 14250)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (5.0, 0, False),
                     (True, 0, False), (10, -1, False), (10, 1.5, False),
                     (10, 0, 1), ("10", 0, False), (None, 0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run(json.dumps({"weight_g": 1000, "distance_km": 101, "express": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 7200})
        for bad in ["{oops", "{}", "[]", json.dumps({"weight_g": 0, "distance_km": 0, "express": False})]:
            p = run(bad)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
