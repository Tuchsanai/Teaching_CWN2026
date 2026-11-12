import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_fee_counts_all_days(self):
        self.assertEqual(late_fee(200, 4), 6)
        self.assertEqual(late_fee(1000, 10), 75)

    def test_half_up(self):
        self.assertEqual(late_fee(200, 5), 8)

    def test_cap(self):
        self.assertEqual(late_fee(1000, 20), 150)
        self.assertEqual(late_fee(1000, 365), 150)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 10), 0)

    def test_invalid(self):
        for a, d in [(5.0, 4), (100, 4.0), (True, 4), (100, False),
                     ("1", 4), (None, 4), (-1, 4), (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"],
                           input='{"amount": 1000, "days_late": 10}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 75})
        for bad in ["{oops", '{"amount": 1}', '{"amount": 1.5, "days_late": 4}']:
            p = subprocess.run([sys.executable, "solve.py"], input=bad,
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
