import json
import subprocess
import sys
import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_1(self): self.assertEqual(f(3000, 150, False), 9600)
    def test_2(self): self.assertEqual(f(1001, 10, False), 8000)
    def test_3(self): self.assertEqual(f(500, 50, False), 4000)
    def test_4(self): self.assertEqual(f(5217, 50, True), 12488)


class Boundary(unittest.TestCase):
    def test_1000(self): self.assertEqual(f(1000, 1, False), 4000)
    def test_5000(self): self.assertEqual(f(5000, 1, False), 8000)
    def test_5001(self): self.assertEqual(f(5001, 1, False), 8002)  # 8000+1.5 -> half-up
    def test_dist_100(self): self.assertEqual(f(3000, 100, False), 8000)
    def test_dist_101(self): self.assertEqual(f(3000, 101, False), 9600)
    def test_dist_zero(self): self.assertEqual(f(3000, 0, False), 0)
    def test_express_20000(self): self.assertEqual(f(20000, 1, True), 45750)
    def test_30000(self): self.assertEqual(f(30000, 1, False), 45500)


class NoDrift(unittest.TestCase):
    def test_1(self): self.assertEqual(f(5106, 150, True), 14686)
    def test_2(self): self.assertEqual(f(5001, 1, False), 8002)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (-1, 1, False), (30001, 1, False), (100.0, 1, False),
                  ("100", 1, False), (True, 1, False), (100, -1, False), (100, 1.0, False),
                  (100, "1", False), (100, 1, 1), (100, 1, "yes"), (20001, 1, True),
                  (20001, 0, True)]:
            with self.subTest(a=a):
                with self.assertRaises(ValueError):
                    f(*a)


class Cli(unittest.TestCase):
    def run_cli(self, p):
        r = subprocess.run([sys.executable, "solve.py"], input=json.dumps(p),
                           capture_output=True, text=True)
        return r.returncode, json.loads(r.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"weight_g": 3000, "distance_km": 150, "express": False}),
                         (0, {"ok": True, "result": 9600}))

    def test_err(self):
        code, out = self.run_cli({"weight_g": 0, "distance_km": 1, "express": False})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
