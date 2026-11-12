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
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 satang -> 2
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_half_up(self):
        # 5001g: 8001.5 satang -> 8002 ; 5003g: 8004.5 -> 8005
        self.assertEqual(shipping_fee(5003, 0, False), 8005)

    def test_distance_express(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)
        # 5001g, far, express: 8001.5*1.8 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_invalid(self):
        bad = [(0, 1, False), (30001, 1, False), (1.0, 1, False), (True, 1, False),
               ("5", 1, False), (None, 1, False), (5, -1, False), (5, 1.5, False),
               (5, True, False), (5, "1", False), (5, None, False),
               (5, 1, 1), (5, 1, None), (5, 1, "True")]
        for a in bad:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_cli(self):
        r = run(json.dumps({"weight_g": 500, "distance_km": 101, "express": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 7200})
        r = run(json.dumps({"weight_g": 0, "distance_km": 1, "express": True}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(run("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
