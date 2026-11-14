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
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8001.5 -> half up
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_rounding_once(self):
        # 8001.5 * 1.5 = 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)
        # 8003 * 1.2 = 9603.6 -> 9604
        self.assertEqual(shipping_fee(5002, 101, False), 9604)

    def test_invalid(self):
        bad = [(0, 0, False), (-1, 0, False), (30001, 0, False),
               (100, -1, False), (100.0, 0, False), (100, 0.0, False),
               (True, 0, False), (100, True, False), ("1", 0, False),
               (100, 0, 1), (100, 0, None), (None, 0, False)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                shipping_fee(*a)


def run(s):
    p = subprocess.run([sys.executable, "solve.py"], input=s,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class TestCLI(unittest.TestCase):
    def test_ok(self):
        c, o, _ = run('{"weight_g": 500, "distance_km": 101, "express": true}')
        self.assertEqual(c, 0)
        self.assertEqual(json.loads(o), {"ok": True, "result": 7200})

    def test_errors(self):
        for s in ['{"weight_g": 0, "distance_km": 1, "express": false}',
                  '{"weight_g": 5.0, "distance_km": 1, "express": false}',
                  '{"weight_g": 5}', 'not json', '[1]']:
            c, o, e = run(s)
            self.assertEqual(c, 2, s)
            self.assertFalse(json.loads(o)["ok"])
            self.assertNotIn("Traceback", e)


if __name__ == "__main__":
    unittest.main()
