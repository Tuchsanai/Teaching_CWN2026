import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tier1(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_tier2(self):
        self.assertEqual(shipping_fee(1001, 10, False), 8000)
        self.assertEqual(shipping_fee(5000, 10, False), 8000)

    def test_over_5kg(self):
        self.assertEqual(shipping_fee(6000, 10, False), 9500)
        self.assertEqual(shipping_fee(5500, 10, False), 8750)
        self.assertEqual(shipping_fee(30000, 10, False), 8000 + 25 * 1500)

    def test_distance_and_express(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)
        self.assertEqual(shipping_fee(1000, 50, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_half_up_once(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (5.0, 1, False),
                     (True, 1, False), (100, -1, False), (100, 1.0, False),
                     (100, 1, 1), ("5", 1, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        self.assertEqual(self._cli('{"weight_g": 1000, "distance_km": 101, "express": true}'),
                         (0, {"ok": True, "result": 7200}))

    def test_cli_errors(self):
        for t in ['not json', '{"weight_g": 1}', '{"weight_g": 0, "distance_km": 1, "express": false}']:
            code, out = self._cli(t)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
