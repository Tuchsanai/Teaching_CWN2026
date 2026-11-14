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
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_distance_express(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1000, 101, False), 4800)
        self.assertEqual(f(1000, 0, True), 6000)
        self.assertEqual(f(1000, 101, True), 7200)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)   # 8001.5
        self.assertEqual(f(5003, 0, False), 8005)   # 8004.5

    def test_errors(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (True, 0, False), (100, 0.0, False),
                  (100, 0, 1), ("1", 0, False), (100, True, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"weight_g":1000,"distance_km":101,"express":true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 7200})
        for s in ['{"weight_g":0,"distance_km":1,"express":false}', 'bad', '{}', '[]']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
