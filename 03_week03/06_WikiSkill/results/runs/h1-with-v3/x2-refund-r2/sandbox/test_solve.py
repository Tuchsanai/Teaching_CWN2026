import json
import os
import subprocess
import sys
import unittest

import solve

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solve.py")


def run_cli(text):
    return subprocess.run([sys.executable, SCRIPT], input=text, capture_output=True, text=True)


class RefundTests(unittest.TestCase):
    def test_no_use_no_restock_full_refund(self):
        self.assertEqual(solve.refund(10000, 0, False), 10000)

    def test_no_use_restock_deducts_fee(self):
        self.assertEqual(solve.refund(10000, 0, True), 8750)

    def test_half_used_no_restock(self):
        self.assertEqual(solve.refund(10000, 50, False), 5000)

    def test_half_used_restock(self):
        self.assertEqual(solve.refund(10000, 50, True), 4375)

    def test_boundary_80_percent_still_refundable(self):
        self.assertEqual(solve.refund(10000, 80, False), 2000)
        self.assertEqual(solve.refund(10000, 80, True), 1750)

    def test_over_80_percent_no_refund(self):
        self.assertEqual(solve.refund(10000, 81, True), 0)
        self.assertEqual(solve.refund(10000, 100, False), 0)

    def test_half_up_rounding_at_final_step_only(self):
        self.assertEqual(solve.refund(1, 50, False), 1)   # ครึ่งสตางค์ ปัดขึ้นเป็น 1
        self.assertEqual(solve.refund(5, 50, False), 3)   # 2 กับครึ่ง ปัดขึ้นเป็น 3
        self.assertEqual(solve.refund(3, 50, True), 1)    # 1 จุด 3125 ปัดลงเป็น 1

    def test_zero_paid(self):
        self.assertEqual(solve.refund(0, 0, True), 0)

    def test_invalid_inputs_raise_value_error(self):
        bad_calls = [
            (float("5"), 0, False),
            (True, 0, False),
            ("100", 0, False),
            (-1, 0, False),
            (100, float(50), False),
            (100, True, False),
            (100, -1, False),
            (100, 101, False),
            (100, 0, 1),
            (100, 0, None),
        ]
        for args in bad_calls:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    solve.refund(*args)


class CliTests(unittest.TestCase):
    def test_cli_success(self):
        proc = run_cli(json.dumps({"paid": 10000, "used_percent": 50, "restock": True}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 4375})

    def test_cli_invalid_value(self):
        proc = run_cli(json.dumps({"paid": 10000, "used_percent": 101, "restock": True}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_json(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli(json.dumps({"paid": 10000, "used_percent": 0}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
