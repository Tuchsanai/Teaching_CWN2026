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

    def test_over_5000(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 -> 2
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 25 * 1500)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_rounding_once(self):
        # 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (5.0, 1, False),
                     (True, 1, False), ("5", 1, False), (None, 1, False),
                     (10, -1, False), (10, 1.0, False), (10, 1, 1), (10, 1, None)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def _run(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout), p.stderr

    def test_cli_ok(self):
        code, out, _ = self._run('{"weight_g": 500, "distance_km": 0, "express": false}')
        self.assertEqual((code, out), (0, {"ok": True, "result": 4000}))

    def test_cli_errors(self):
        for t in ['not json', '{"weight_g": 5}', '[]',
                  '{"weight_g": 5.0, "distance_km": 1, "express": true}']:
            code, out, err = self._run(t)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
