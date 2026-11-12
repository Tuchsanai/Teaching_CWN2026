import json
import os
import subprocess
import sys
import unittest

from solve import late_fee

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


def run_cli(text):
    return subprocess.run(
        [sys.executable, SOLVE],
        input=text,
        capture_output=True,
        text=True,
    )


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_grace_period(self):
        for days in range(0, 4):
            self.assertEqual(late_fee(1000, days), 0)

    def test_fee_from_day_4_counts_all_days(self):
        # 1000 * 4 * 0.75% = 30 สตางค์
        self.assertEqual(late_fee(1000, 4), 30)

    def test_half_up_rounding_at_final_step(self):
        # 200 * 5 * 0.75% = 7.5 -> ปัดขึ้นเป็น 8
        self.assertEqual(late_fee(200, 5), 8)

    def test_cap_15_percent(self):
        # 21 วัน = 15.75% จึงถูกจำกัดที่ 15% = 150
        self.assertEqual(late_fee(1000, 21), 150)
        self.assertEqual(late_fee(1000, 365), 150)

    def test_day_20_equals_cap_exactly(self):
        # 20 วัน = 15% พอดี
        self.assertEqual(late_fee(1000, 20), 150)

    def test_zero_amount_gives_zero_fee(self):
        self.assertEqual(late_fee(0, 30), 0)

    def test_invalid_input_raises_value_error(self):
        bad_calls = [
            (1000.0, 5),
            (1000, 5.0),
            (True, 5),
            (1000, False),
            ("1000", 5),
            (None, 5),
            (-1, 5),
            (1000, -1),
            (1000, 366),
        ]
        for amount, days in bad_calls:
            with self.subTest(amount=amount, days=days):
                with self.assertRaises(ValueError):
                    late_fee(amount, days)


class TestCli(unittest.TestCase):
    def test_cli_success_output(self):
        proc = run_cli(json.dumps({"amount": 1000, "days_late": 4}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 30})

    def test_cli_invalid_json_exit_2_without_traceback(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_cli_missing_key_exit_2(self):
        proc = run_cli(json.dumps({"amount": 1000}))
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertIn("days_late", out["error"])

    def test_cli_wrong_type_exit_2(self):
        proc = run_cli(json.dumps({"amount": 1000.0, "days_late": 4}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
