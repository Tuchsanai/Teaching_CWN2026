import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_grace_period(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_day_four_counts_all_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap_at_15_percent(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_round_half_up(self):
        # 200*0.03 = 6; 10*0.03=0.3 -> 0; 50*0.03=1.5 -> 2
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(50, 4), 2)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_invalid_inputs(self):
        for a, d in [(-1, 5), (10, -1), (10, 366), (1.5, 5), (10, 4.0),
                     (True, 5), (10, True), ("1", 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"],
                           input=json.dumps({"amount": 100000, "days_late": 4}),
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 3000})

    def test_cli_error(self):
        p = subprocess.run([sys.executable, "solve.py"], input="{bad",
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
