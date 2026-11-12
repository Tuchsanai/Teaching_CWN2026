import json
import os
import subprocess
import sys
import unittest

from solve import bulk_price

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


def run_cli(stdin_text):
    proc = subprocess.run(
        [sys.executable, SOLVE], input=stdin_text, capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


class BulkPriceTests(unittest.TestCase):
    def test_no_discount_adds_vat(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_qty_9_gets_no_bulk_discount(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)

    def test_qty_10_gets_3_5_percent(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_qty_49_still_3_5_percent_with_half_up(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_qty_50_gets_7_5_percent_only(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_max_qty(self):
        self.assertEqual(bulk_price(100, 1000, False), 98975)

    def test_coupon_only(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_coupon_stacks_with_bulk(self):
        self.assertEqual(bulk_price(40000, 10, True), 402695)

    def test_zero_price_is_allowed(self):
        self.assertEqual(bulk_price(0, 1, True), 0)

    def test_invalid_inputs_raise_value_error(self):
        bad_args = [
            (1.5, 1, False), (5.0, 1, False), (-1, 1, False), (True, 1, False),
            ("100", 1, False), (None, 1, False),
            (100, 0, False), (100, 1001, False), (100, True, False), (100, 1.0, False),
            (100, 1, "yes"), (100, 1, 1),
        ]
        for args in bad_args:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)

    def test_cli_success(self):
        code, out, _ = run_cli(json.dumps({"unit_price": 10000, "qty": 1, "coupon": False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 10700})

    def test_cli_invalid_json_exit_2_no_traceback(self):
        code, out, err = run_cli("{bad json")
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_cli_missing_key_exit_2(self):
        code, out, _ = run_cli(json.dumps({"unit_price": 100, "qty": 1}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])


if __name__ == "__main__":
    unittest.main()
