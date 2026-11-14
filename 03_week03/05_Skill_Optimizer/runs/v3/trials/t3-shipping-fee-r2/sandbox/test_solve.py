import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_excess(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5500, 0, False), 8750)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_bad_values(self):
        for args in [(0, 0, False), (30001, 0, False), (10, -1, False),
                     (10.0, 0, False), (True, 0, False), ("1", 0, False),
                     (10, None, False), (10, 0, 1), (10, 0, None)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        self.assertEqual(self._cli('{"weight_g": 500, "distance_km": 0, "express": true}'),
                         (0, {"ok": True, "result": 6000}))

    def test_cli_errors(self):
        for t in ['not json', '{"weight_g": 5}', '[]',
                  '{"weight_g": 5.0, "distance_km": 0, "express": false}']:
            code, out = self._cli(t)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
