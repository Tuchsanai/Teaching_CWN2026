import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_tier_10(self):
        self.assertEqual(bulk_price(2000, 10, False), 20651)

    def test_tier_50_single_rate(self):
        self.assertEqual(bulk_price(2000, 50, False), 98975)

    def test_coupon_only(self):
        self.assertEqual(bulk_price(4000, 1, True), 4173)

    def test_half_up_rounding(self):
        self.assertEqual(bulk_price(8000, 50, True), 386003)

    def test_invalid_inputs(self):
        for args in [(1.0, 1, False), (True, 1, False), (-1, 1, False),
                     (100, 0, False), (100, 1001, False), (100, "1", False),
                     (100, 1, 1), (100, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli(self):
        ok = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                            input=json.dumps({"unit_price": 1000, "qty": 1, "coupon": False}))
        self.assertEqual(ok.returncode, 0)
        self.assertEqual(json.loads(ok.stdout), {"ok": True, "result": 1070})
        for bad in ["not json", "{}", "[1]", json.dumps({"unit_price": 1, "qty": 0, "coupon": True})]:
            r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input=bad)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertEqual(r.stderr, "")


if __name__ == "__main__":
    unittest.main()
