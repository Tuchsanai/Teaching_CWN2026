import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_3_days(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_day4_counts_all_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)  # 4*0.75% = 3%

    def test_cap_boundary(self):
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_rounding(self):
        self.assertEqual(late_fee(10, 4), 0)    # 0.3 -> 0
        self.assertEqual(late_fee(50, 4), 2)    # 1.5 -> 2
        self.assertEqual(late_fee(0, 10), 0)

    def test_invalid(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     (True, 5), (100, True), ("100", 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_invalid_before_early_return(self):
        with self.assertRaises(ValueError):
            late_fee(-5, 0)

    def _cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=payload,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self._cli('{"amount": 100000, "days_late": 4}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 3000})

    def test_cli_error(self):
        r = self._cli('{"amount": -1, "days_late": 4}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
