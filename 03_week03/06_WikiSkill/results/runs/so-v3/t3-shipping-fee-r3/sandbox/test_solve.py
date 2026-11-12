import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class TestShippingFee(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_over_5kg(self):
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5002, 0, False), 8003)

    def test_distance(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_express(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (5.0, 0, False),
                     (True, 0, False), (10, -1, False), (10, 0, 1), (10, "1", False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"weight_g":6000,"distance_km":0,"express":false}',
                           capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 9500})
        r = subprocess.run([sys.executable, "solve.py"], input='{bad', capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
