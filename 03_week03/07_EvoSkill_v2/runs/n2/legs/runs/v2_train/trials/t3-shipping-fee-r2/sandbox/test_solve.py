import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class Normal(unittest.TestCase):
    def test_1(self): self.assertEqual(shipping_fee(3000, 150, False), 9600)
    def test_2(self): self.assertEqual(shipping_fee(500, 10, False), 4000)
    def test_3(self): self.assertEqual(shipping_fee(500, 150, True), 7200)
    def test_4(self): self.assertEqual(shipping_fee(20000, 10, True), 45750)


class Boundary(unittest.TestCase):
    def test_1000(self): self.assertEqual(shipping_fee(1000, 10, False), 4000)
    def test_1001(self): self.assertEqual(shipping_fee(1001, 10, False), 8000)
    def test_5000(self): self.assertEqual(shipping_fee(5000, 10, False), 8000)
    def test_dist_100(self): self.assertEqual(shipping_fee(1000, 100, False), 4000)
    def test_dist_101(self): self.assertEqual(shipping_fee(1000, 101, False), 4800)
    def test_dist_0(self): self.assertEqual(shipping_fee(30000, 0, False), 0)
    def test_max(self): self.assertEqual(shipping_fee(30000, 1, False), 45500)
    def test_express_20000_ok(self): self.assertEqual(shipping_fee(20000, 1, True), 45750)
    def test_express_20001(self):
        with self.assertRaises(ValueError):
            shipping_fee(20001, 1, True)
    def test_express_over_with_dist0(self):
        with self.assertRaises(ValueError):
            shipping_fee(25000, 0, True)


class NoDrift(unittest.TestCase):
    def test_1(self): self.assertEqual(shipping_fee(5001, 10, False), 8002)  # 8001.5
    def test_2(self): self.assertEqual(shipping_fee(5106, 150, True), 14686)
    def test_3(self): self.assertEqual(shipping_fee(5217, 50, True), 12488)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(0, 1, False), (-1, 1, False), (30001, 1, False), (100.0, 1, False),
                     ("100", 1, False), (True, 1, False), (100, -1, False), (100, 1.5, False),
                     (100, "5", False), (100, 1, 1), (100, 1, None), (100, 1, "yes")]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    shipping_fee(*args)


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
