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

    def test_over_5000_proportional(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 -> half-up
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express_and_combined(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (5.0, 0, False),
                     (True, 0, False), (10, -1, False), (10, 1.0, False),
                     (10, 0, 1), ("5", 0, False), (None, 0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        def run(s):
            p = subprocess.run([sys.executable, "solve.py"], input=s,
                               capture_output=True, text=True)
            return p.returncode, json.loads(p.stdout)
        self.assertEqual(run('{"weight_g":500,"distance_km":0,"express":false}'),
                         (0, {"ok": True, "result": 4000}))
        self.assertEqual(run("nope")[0], 2)
        self.assertEqual(run('{"weight_g":1}')[1]["ok"], False)


if __name__ == "__main__":
    unittest.main()
