import json
import subprocess
import sys
import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_1(self): self.assertEqual(f(3000, 150, False), 9600)
    def test_2(self): self.assertEqual(f(500, 10, False), 4000)
    def test_3(self): self.assertEqual(f(10000, 50, False), 15500)
    def test_4(self): self.assertEqual(f(3000, 50, True), 12000)


class Boundary(unittest.TestCase):
    def test_1000(self): self.assertEqual(f(1000, 10, False), 4000)
    def test_1001(self): self.assertEqual(f(1001, 10, False), 8000)
    def test_5000(self): self.assertEqual(f(5000, 10, False), 8000)
    def test_5001(self): self.assertEqual(f(5001, 10, False), 8002)  # 8000+1.5=8001.5 -> half-up
    def test_100(self): self.assertEqual(f(1000, 100, False), 4000)
    def test_101(self): self.assertEqual(f(1000, 101, False), 4800)
    def test_zero_distance(self): self.assertEqual(f(3000, 0, False), 0)
    def test_express_20000(self): self.assertEqual(f(20000, 10, True), 45750)


class NoDrift(unittest.TestCase):
    def test_1(self): self.assertEqual(f(5106, 150, True), 14686)
    def test_2(self): self.assertEqual(f(5217, 50, True), 12488)
    def test_3(self): self.assertEqual(f(30000, 10, False), 45500)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            f(*a)

    def test_w0(self): self.bad(0, 10, False)
    def test_w_big(self): self.bad(30001, 10, False)
    def test_w_float(self): self.bad(1000.0, 10, False)
    def test_w_str(self): self.bad("1000", 10, False)
    def test_w_bool(self): self.bad(True, 10, False)
    def test_d_neg(self): self.bad(1000, -1, False)
    def test_d_float(self): self.bad(1000, 10.5, False)
    def test_d_bool(self): self.bad(1000, True, False)
    def test_express_not_bool(self): self.bad(1000, 10, 1)
    def test_express_heavy(self): self.bad(20001, 10, True)
    def test_express_heavy_zero_dist(self): self.bad(25000, 0, True)
    def test_invalid_before_zero_dist(self): self.bad(0, 0, False)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"weight_g": 3000, "distance_km": 150, "express": False}),
                         (0, {"ok": True, "result": 9600}))

    def test_error(self):
        code, out = self.run_cli({"weight_g": 0, "distance_km": 1, "express": False})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
