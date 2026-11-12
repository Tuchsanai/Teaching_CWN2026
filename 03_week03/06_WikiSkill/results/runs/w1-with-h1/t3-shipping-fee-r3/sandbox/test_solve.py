import json
import subprocess
import sys
import unittest
from solve import shipping_fee


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8000+1.5 -> half up
        self.assertEqual(shipping_fee(5002, 0, False), 8003)
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 25 * 1500)

    def test_distance(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_express_and_combined(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)
        # 8001.5*1.5 = 12002.25 -> 12002 (single rounding)
        self.assertEqual(shipping_fee(5001, 0, True), 12002)
        # 8001.5*1.2*1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 200, True), 14403)

    def test_invalid(self):
        bad = [(0, 0, False), (30001, 0, False), (-1, 0, False), (1.0, 0, False),
               (True, 0, False), ("5", 0, False), (None, 0, False),
               (100, -1, False), (100, 1.5, False), (100, True, False),
               (100, "1", False), (100, None, False),
               (100, 0, 1), (100, 0, None), (100, 0, "True")]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                shipping_fee(*a)

    def test_cli(self):
        r = run(json.dumps({"weight_g": 5001, "distance_km": 0, "express": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 12002})
        for p in ['{"weight_g": 0, "distance_km": 0, "express": false}', 'nope', '{}']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
