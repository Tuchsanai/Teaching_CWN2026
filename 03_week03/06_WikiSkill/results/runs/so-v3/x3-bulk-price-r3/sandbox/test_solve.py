import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier_10(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier_50_single_rate(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon_half_up(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundary_9_vs_10(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_invalid(self):
        for args in [(1.0, 1, False), (True, 1, False), (-1, 1, False),
                     (100, 0, False), (100, 1001, False), (100, 1.0, False),
                     (100, 1, 1), (100, 1, None), ("1", 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def run_cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self.run_cli('{"unit_price": 10000, "qty": 1, "coupon": false}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 10700})

    def test_cli_errors(self):
        for t in ["not json", '{"unit_price": 1}', '[1]',
                  '{"unit_price": 5.0, "qty": 1, "coupon": false}']:
            code, out, err = self.run_cli(t)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
