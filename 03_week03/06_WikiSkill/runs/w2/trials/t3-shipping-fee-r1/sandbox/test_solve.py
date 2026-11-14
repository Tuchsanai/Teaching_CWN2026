import json
import subprocess
import sys
import unittest

from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)

    def test_over5000(self):
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 25 * 1500)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half up

    def test_distance(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)
        self.assertEqual(f(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)
        self.assertEqual(f(6000, 101, True), 17100)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (1.0, 0, False),
                  (True, 0, False), (100, -1, False), (100, "1", False),
                  (100, True, False), (100, float("nan"), False),
                  (100, 0, 1), (100, 0, "yes"), ("100", 0, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input='{"weight_g": 500, "distance_km": 0, "express": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 6000})
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input='{"weight_g": -5, "distance_km": 0, "express": true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
