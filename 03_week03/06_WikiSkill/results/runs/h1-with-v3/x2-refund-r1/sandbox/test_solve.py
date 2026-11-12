import json
import os
import subprocess
import sys
import unittest

from solve import refund

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


class RefundTest(unittest.TestCase):
    def test_no_usage_full_refund_without_restock(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_proportional_refund(self):
        self.assertEqual(refund(10000, 30, False), 7000)

    def test_exactly_80_percent_still_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_over_80_percent_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_restock_fee_12_5_percent(self):
        self.assertEqual(refund(8000, 0, True), 7000)
        self.assertEqual(refund(8000, 50, True), 3500)

    def test_half_up_rounding_at_end(self):
        self.assertEqual(refund(4, 0, True), 4)    # 3.5 -> 4
        self.assertEqual(refund(1, 0, True), 1)    # 0.875 -> 1
        self.assertEqual(refund(50, 1, False), 50)  # 49.5 -> 50

    def test_invalid_inputs_raise_value_error(self):
        bad_calls = [
            (-1, 0, False),
            (5.0, 0, False),
            (100, 101, False),
            (100, -1, False),
            (100, 5.0, False),
            (100, True, False),
            (100, 0, "yes"),
            (None, 0, False),
        ]
        for args in bad_calls:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    refund(*args)

    def _run_cli(self, text):
        return subprocess.run(
            [sys.executable, SOLVE],
            input=text,
            capture_output=True,
            text=True,
        )

    def test_cli_success(self):
        p = self._run_cli(json.dumps({"paid": 8000, "used_percent": 0, "restock": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 7000})

    def test_cli_errors_exit_2_without_traceback(self):
        for text in ["{not json", json.dumps({"paid": 100, "used_percent": 0}),
                     json.dumps([1, 2]), json.dumps({"paid": 1.5, "used_percent": 0, "restock": False})]:
            with self.subTest(text=text):
                p = self._run_cli(text)
                self.assertEqual(p.returncode, 2)
                self.assertNotIn("Traceback", p.stdout + p.stderr)
                out = json.loads(p.stdout)
                self.assertFalse(out["ok"])
                self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
