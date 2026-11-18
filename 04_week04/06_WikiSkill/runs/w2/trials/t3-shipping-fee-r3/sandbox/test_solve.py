import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)

    def test_fraction_gram(self):
        # 5001 g -> 8000 + 1.5 = 8001.5 -> half up 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_distance(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1000, 101, False), 4800)
        self.assertEqual(shipping_fee(1000, 100.5, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 150, True), 7200)

    def test_rounding_once(self):
        # (8000+1.5)*1.2*1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_invalid(self):
        bad = [(0, 0, False), (30001, 0, False), (-1, 0, False),
               (1.0, 0, False), (True, 0, False), ("5", 0, False),
               (None, 0, False), (100, -1, False), (100, True, False),
               (100, "5", False), (100, float("nan"), False),
               (100, 0, 1), (100, 0, "yes"), (100, 0, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                shipping_fee(*a)

    def run_cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=payload,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli(json.dumps({"weight_g": 1000, "distance_km": 0, "express": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 6000})

    def test_cli_error(self):
        r = self.run_cli(json.dumps({"weight_g": 0, "distance_km": 0, "express": True}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)
        r = self.run_cli("not json")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
