import json
import os
import subprocess
import sys
import unittest

from solve import late_fee

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "solve.py")


def run_cli(text):
    return subprocess.run(
        [sys.executable, SCRIPT],
        input=text,
        capture_output=True,
        text=True,
    )


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_grace_period(self):
        for days in (0, 1, 2, 3):
            self.assertEqual(late_fee(10000, days), 0)

    def test_daily_rate_counts_all_days_including_first_three(self):
        self.assertEqual(late_fee(10000, 4), 300)
        self.assertEqual(late_fee(10000, 10), 750)

    def test_half_up_rounding_at_final_step(self):
        self.assertEqual(late_fee(50, 4), 2)      # 1.5 -> 2
        self.assertEqual(late_fee(1000, 19), 143)  # 142.5 -> 143

    def test_cap_15_percent(self):
        self.assertEqual(late_fee(1000, 20), 150)
        self.assertEqual(late_fee(1000, 21), 150)
        self.assertEqual(late_fee(1000, 365), 150)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_rejects_wrong_types(self):
        for bad in (json.loads("1.0"), True, "3", None):
            with self.assertRaises(ValueError):
                late_fee(bad, 5)
            with self.assertRaises(ValueError):
                late_fee(1000, bad)

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)
        with self.assertRaises(ValueError):
            late_fee(1000, -1)
        with self.assertRaises(ValueError):
            late_fee(1000, 366)

    def test_cli_success(self):
        proc = run_cli(json.dumps({"amount": 10000, "days_late": 4}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 300})

    def test_cli_errors_exit_2_without_traceback(self):
        cases = [
            "{not json",
            json.dumps({"amount": 1000}),
            json.dumps({"amount": 5.0, "days_late": 4}),
            json.dumps([1, 2]),
        ]
        for text in cases:
            proc = run_cli(text)
            self.assertEqual(proc.returncode, 2, text)
            self.assertFalse(json.loads(proc.stdout)["ok"])
            self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
