import json
import subprocess
import sys
import unittest

from solve import late_fee


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_grace(self):
        for d in (0, 1, 3):
            self.assertEqual(late_fee(100000, d), 0)

    def test_day4_counts_all_days(self):
        # 100000 * 0.0075 * 4 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        # 20 days = 15% exactly; 30 days capped at 15%
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        # 200*0.0075*4 = 6.0 ; 2*... use 10 * 75 * 5 /10000 = 0.375 -> 0
        self.assertEqual(late_fee(10, 5), 0)
        # 100*75*7/10000 = 5.25 -> 5
        self.assertEqual(late_fee(100, 7), 5)
        # 200*75*5/10000 = 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_cap_half_up(self):
        # cap 15% of 10 = 1.5 -> 2; fee 10*75*365/10000=27.4 -> capped 2
        self.assertEqual(late_fee(10, 365), 2)

    def test_invalid(self):
        for a, d in [(1.0, 5), (True, 5), ("1", 5), (None, 5), (-1, 5),
                     (100, 5.0), (100, True), (100, "5"), (100, None),
                     (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        r = run(json.dumps({"amount": 100000, "days_late": 4}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 3000})
        r = run(json.dumps({"amount": 1.5, "days_late": 4}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(run("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
