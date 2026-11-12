import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from solve import late_fee  # noqa: E402

SOLVE = os.path.join(HERE, "solve.py")


def run_cli(raw):
    return subprocess.run(
        [sys.executable, SOLVE], input=raw, capture_output=True, text=True
    )


class LateFeeTests(unittest.TestCase):
    def test_no_fee_within_grace_period(self):
        for days in range(0, 4):
            self.assertEqual(late_fee(10000, days), 0)

    def test_fourth_day_charged_including_first_three(self):
        # 10000 * 75/10000 * 4 = 300 (ต่ำกว่าเพดาน 1500)
        self.assertEqual(late_fee(10000, 4), 300)

    def test_linear_before_cap(self):
        self.assertEqual(late_fee(10000, 10), 750)

    def test_cap_exact_at_20_days(self):
        self.assertEqual(late_fee(10000, 20), 1500)

    def test_cap_applies_for_long_delay(self):
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_half_up_rounding_once(self):
        # 20 * 75/10000 * 10 = 1.5 -> 2 ; เพดาน = 3
        self.assertEqual(late_fee(20, 10), 2)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 365), 0)

    def test_invalid_inputs_raise_value_error(self):
        bad_args = [
            (5.0, 4), (True, 4), (10000, 4.0), (10000, True),
            (-1, 4), (10000, -1), (10000, 366), ("100", 4), (None, 4),
        ]
        for args in bad_args:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    late_fee(*args)

    def test_cli_success(self):
        p = run_cli(json.dumps({"amount": 10000, "days_late": 4}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 300})

    def test_cli_errors_exit_2_without_traceback(self):
        cases = [
            "not json",
            json.dumps({"amount": 10000}),
            json.dumps([1, 2]),
            json.dumps({"amount": 10000, "days_late": 400}),
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                p = run_cli(raw)
                self.assertEqual(p.returncode, 2)
                out = json.loads(p.stdout)
                self.assertFalse(out["ok"])
                self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
