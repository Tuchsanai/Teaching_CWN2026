import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_over_5000(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8001.5 rounds up

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 150, True), 7200)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (10, -1, False),
                     (10.0, 1, False), (True, 1, False), (10, 1, 1), ("1", 1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run(json.dumps({"weight_g": 500, "distance_km": 0, "express": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4000})
        for bad in ["nope", "{}", json.dumps({"weight_g": 0, "distance_km": 0, "express": False})]:
            p = run(bad)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
