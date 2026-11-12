import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_excess_proportional(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 -> half up
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (5, -1, False),
                     (5.0, 0, False), (True, 0, False), ("5", 0, False),
                     (5, None, False), (5, 0, 1), (5, 0, None), (5, 1.0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def run_cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self.run_cli('{"weight_g": 500, "distance_km": 101, "express": true}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 7200})

    def test_cli_errors(self):
        for text in ["not json", "{}", '{"weight_g": 5.0, "distance_km": 1, "express": false}', "[1]"]:
            code, out, err = self.run_cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
