import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_day_four_counts_all_days(self):
        self.assertEqual(late_fee(10000, 4), 300)

    def test_cap_at_15_percent(self):
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_half_up_rounding(self):
        # 200 * 4 * 75 = 60000 over 10000 = 6 exactly
        self.assertEqual(late_fee(200, 4), 6)
        # 2 * 10 * 75 = 1500 over 10000, below half -> 0
        self.assertEqual(late_fee(2, 10), 0)
        # 100 * 5 * 75 = 37500 over 10000 = 3.75 -> 4
        self.assertEqual(late_fee(100, 5), 4)

    def test_invalid_inputs(self):
        for a, d in [(-1, 5), (10, -1), (10, 366), (1.0, 5), (10, 5.0),
                     (True, 5), (10, False), ("10", 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def _run(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self._run('{"amount": 10000, "days_late": 4}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 300})

    def test_cli_errors(self):
        for text in ["not json", "{}", '{"amount": 1}', "[1]",
                     '{"amount": 5.0, "days_late": 4}']:
            code, out, err = self._run(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
