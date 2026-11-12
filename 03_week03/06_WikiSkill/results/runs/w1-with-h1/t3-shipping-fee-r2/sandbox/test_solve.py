import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_over_5000(self):
        # 8000 + 1 g * 1.5 satang = 8001.5 -> 8002 (half up)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)
        self.assertEqual(shipping_fee(5002, 0, False), 8003)
        # 30000: 8000 + 25*1500 = 45500
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance_boundary(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_single_rounding(self):
        # 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)
        # 8001.5 * 1.5 = 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    def test_invalid(self):
        bad = [
            (0, 0, False), (30001, 0, False), (-1, 0, False),
            (1000.0, 0, False), (True, 0, False), ("1000", 0, False), (None, 0, False),
            (1000, -1, False), (1000, 1.5, False), (1000, True, False),
            (1000, "5", False), (1000, None, False),
            (1000, 0, 1), (1000, 0, 0), (1000, 0, None), (1000, 0, "True"),
        ]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                shipping_fee(*args)

    def run_cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=payload,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli(json.dumps({"weight_g": 5001, "distance_km": 101, "express": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 14403})

    def test_cli_error(self):
        for p in ['{"weight_g": 0, "distance_km": 0, "express": false}', "not json", "[]",
                  '{"weight_g": 10}']:
            r = self.run_cli(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
