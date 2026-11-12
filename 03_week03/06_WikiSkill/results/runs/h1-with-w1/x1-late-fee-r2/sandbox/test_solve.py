import json
import os
import subprocess
import sys
import unittest

from solve import late_fee

HERE = os.path.dirname(os.path.abspath(__file__))


class TestLateFee(unittest.TestCase):
    def test_grace_period_no_fee(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 1), 0)
        self.assertEqual(late_fee(100000, 3), 0)   # พอดี 3 วัน ยังไม่คิด

    def test_first_day_over_grace(self):
        # 4 วัน: 100000 * 0.75% * 4 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_normal_value_counts_all_days(self):
        # 10 วัน: 100000 * 0.75% * 10 = 7500 (ไม่ตัด 3 วันแรก)
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap_15_percent(self):
        # 0.75% * 20 = 15% พอดี; 30 วัน ต้องถูกจำกัดที่ 15%
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up_rounding(self):
        # fee = amount * 3 * days / 400
        self.assertEqual(late_fee(1, 4), 0)      # 0.03 -> 0
        self.assertEqual(late_fee(10, 6), 0)     # 0.45 -> 0 (ต่ำกว่า .5)
        self.assertEqual(late_fee(20, 6), 1)     # 0.90 -> 1
        self.assertEqual(late_fee(40, 4), 1)     # 1.20 -> 1
        self.assertEqual(late_fee(100, 6), 5)    # 4.50 -> 5 (.5 ปัดขึ้น)
        self.assertEqual(late_fee(200, 5), 8)    # 7.50 -> 8 (.5 ปัดขึ้น)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)
        with self.assertRaises(ValueError):
            late_fee(100, -1)
        with self.assertRaises(ValueError):
            late_fee(100, 366)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            late_fee(100.0, 5)
        with self.assertRaises(ValueError):
            late_fee(100, 5.0)

    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)
        with self.assertRaises(ValueError):
            late_fee(100, False)

    def test_reject_str_none(self):
        with self.assertRaises(ValueError):
            late_fee('100', 5)
        with self.assertRaises(ValueError):
            late_fee(100, None)


class TestCli(unittest.TestCase):
    def run_cli(self, payload):
        return subprocess.run(
            [sys.executable, os.path.join(HERE, 'solve.py')],
            input=json.dumps(payload), capture_output=True, text=True, cwd=HERE,
        )

    def test_cli_ok(self):
        p = self.run_cli({'amount': 100000, 'days_late': 10})
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {'ok': True, 'result': 7500})

    def test_cli_error(self):
        p = self.run_cli({'amount': 100000, 'days_late': 400})
        self.assertEqual(p.returncode, 2)
        out = json.loads(p.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', p.stderr)


if __name__ == '__main__':
    unittest.main()
