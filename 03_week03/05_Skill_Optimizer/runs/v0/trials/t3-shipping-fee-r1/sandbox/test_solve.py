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
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 25 * 1500)

    def test_fraction_rounding(self):
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 -> half up
        self.assertEqual(f(5003, 0, False), 8005)  # 4.5

    def test_distance(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_express(self):
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 1, False), (30001, 1, False), (True, 1, False), ("5", 1, False),
                  (10, -1, False), (10, float("nan"), False), (10, 1, 1), (10, None, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"weight_g": 500, "distance_km": 101, "express": True}))
        self.assertEqual(json.loads(r.stdout), {"fee_satang": 7200})
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input='{"weight_g":0}')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("error", json.loads(r.stdout))


if __name__ == "__main__":
    unittest.main()
