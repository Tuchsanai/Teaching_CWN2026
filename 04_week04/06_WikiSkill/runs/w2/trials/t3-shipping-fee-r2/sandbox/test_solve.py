import json
import subprocess
import sys
import unittest

from solve import shipping_fee as f


class TestFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 25 * 1500)

    def test_fraction_gram_rounding(self):
        # 5001 g -> 8000 + 1.5 = 8001.5 -> 8002
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5002, 0, False), 8003)

    def test_distance(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1000, 100.5, False), 4800)
        self.assertEqual(f(1000, 101, False), 4800)

    def test_express(self):
        self.assertEqual(f(1000, 0, True), 6000)
        self.assertEqual(f(1000, 101, True), 7200)
        # 8001.5 * 1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)
        # 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403
        self.assertEqual(f(5001, 101, True), 14403)

    def test_invalid(self):
        bad = [
            (0, 0, False), (30001, 0, False), (-5, 0, False),
            (1000, -1, False), (1000.0, 0, False), (True, 0, False),
            ("1000", 0, False), (1000, True, False), (1000, "1", False),
            (1000, float("nan"), False), (1000, 0, 1), (1000, 0, "yes"),
            (1000, 0, None),
        ]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                f(*a)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli('{"weight_g": 1000, "distance_km": 0, "express": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 6000})

    def test_cli_bad(self):
        for t in ['{"weight_g": -1, "distance_km": 0, "express": false}',
                  'not json', '[1]', '{"weight_g": 5}']:
            r = self.run_cli(t)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
