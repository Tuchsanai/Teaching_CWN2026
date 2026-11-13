import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_light(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_mid(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_over_weight(self):
        self.assertEqual(shipping_fee(7000, 10, False), 11000)

    def test_far(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_express_far(self):
        self.assertEqual(shipping_fee(5000, 200, True), 14400)

    def test_half_up(self):
        # 5001 g: 8000 + 1.5 = 8001.5 -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (1.0, 1, False),
                     (True, 1, False), (1, -1, False), (1, 1, 1), (1, "1", False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run(json.dumps({"weight_g": 500, "distance_km": 5, "express": True}))
        self.assertEqual((p.returncode, json.loads(p.stdout)), (0, {"ok": True, "result": 6000}))
        for bad in ["{oops", "{}", json.dumps({"weight_g": 0, "distance_km": 1, "express": False})]:
            p = run(bad)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
