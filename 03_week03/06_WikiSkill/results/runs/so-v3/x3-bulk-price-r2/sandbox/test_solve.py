import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)

    def test_below_tier(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)

    def test_tier_10(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_tier_50_single_rate(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_coupon(self):
        self.assertEqual(bulk_price(2000, 1, True), 2087)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_invalid(self):
        for args in [(-1, 1, False), (1.0, 1, False), (True, 1, False),
                     (100, 0, False), (100, 1001, False), (100, 1.0, False),
                     (100, 1, 1), (100, 1, None), ("1", 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run('{"unit_price": 1000, "qty": 1, "coupon": false}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 1070})
        for bad in ['{bad', '{"qty": 1}', '[]', '{"unit_price": 1, "qty": 0, "coupon": true}']:
            p = run(bad)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
