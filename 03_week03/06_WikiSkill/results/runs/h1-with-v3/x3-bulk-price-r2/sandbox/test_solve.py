import json
import os
import subprocess
import sys
import unittest

from solve import bulk_price

SOLVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solve.py")


def run_cli(payload_text):
    return subprocess.run(
        [sys.executable, SOLVE_PATH],
        input=payload_text,
        capture_output=True,
        text=True,
    )


class TestBulkPrice(unittest.TestCase):
    def test_single_bag_no_coupon_adds_vat(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier_10_bags_gets_3_5_percent(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier_50_bags_gets_7_5_percent_only_once(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_boundary_9_has_no_discount_and_49_rounds_half_up(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5 -> 505950

    def test_coupon_stacks_after_bulk_and_rounds_half_up(self):
        self.assertEqual(bulk_price(4000, 1, True), 4173)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 -> 10433

    def test_zero_price_and_invalid_inputs(self):
        self.assertEqual(bulk_price(0, 1, True), 0)
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(float(10000), 1, False)
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(10000, 0, False)
        with self.assertRaises(ValueError):
            bulk_price(10000, 1001, False)
        with self.assertRaises(ValueError):
            bulk_price(10000, False, False)
        with self.assertRaises(ValueError):
            bulk_price(10000, 1, 1)


class TestCli(unittest.TestCase):
    def test_cli_success(self):
        proc = run_cli(json.dumps({"unit_price": 10000, "qty": 50, "coupon": False}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 494875})

    def test_cli_invalid_value_exit_2_without_traceback(self):
        proc = run_cli(json.dumps({"unit_price": 10000, "qty": 0, "coupon": False}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_json_and_missing_key_exit_2(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)
        proc = run_cli(json.dumps({"unit_price": 10000, "qty": 1}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
