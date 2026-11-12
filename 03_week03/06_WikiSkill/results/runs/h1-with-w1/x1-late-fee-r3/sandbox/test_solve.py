import json
import subprocess
import sys
import unittest

from solve import late_fee


def run_cli(payload):
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestLateFee(unittest.TestCase):

    # --- ช่วงผ่อนผัน 3 วัน ---
    def test_no_fee_within_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 1), 0)
        self.assertEqual(late_fee(100000, 3), 0)  # ขอบพอดี

    def test_fee_starts_day_4_counting_all_days(self):
        # 4 วัน: 100000 * 0.75% * 4 = 3000
        self.assertEqual(late_fee(100000, 4), 3000)

    # --- ปกติ ---
    def test_normal_case(self):
        # 10 วัน: 100000 * 0.0075 * 10 = 7500
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)

    # --- เพดาน 15% ---
    def test_cap_exact_boundary(self):
        # 20 วัน: 0.75% * 20 = 15% พอดี
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_cap_applies_above_boundary(self):
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_just_below_cap(self):
        # 19 วัน: 0.75% * 19 = 14.25%
        self.assertEqual(late_fee(100000, 19), 14250)

    # --- half-up ---
    def test_half_up_rounds_point_five_up(self):
        # amount=10, 4 วัน: 10 * 0.0075 * 4 = 0.30 -> 0
        self.assertEqual(late_fee(10, 4), 0)
        # amount=60, 4 วัน: 60 * 0.03 = 1.8 -> 2
        self.assertEqual(late_fee(60, 4), 2)
        # amount=70, 4 วัน: 70 * 0.03 = 2.1 -> 2
        self.assertEqual(late_fee(70, 4), 2)
        # ต้องการทดสอบ .5 พอดี: amount=50, 4 วัน: 50*0.03 = 1.5 -> 2 (half-up)
        self.assertEqual(late_fee(50, 4), 2)
        # amount=30, 4 วัน: 30*0.03 = 0.9 -> 1
        self.assertEqual(late_fee(30, 4), 1)

    def test_no_drift_single_rounding(self):
        # ปัดครั้งเดียวตอนท้าย: amount=333, 7 วัน
        # 333 * 0.0075 * 7 = 17.4825 -> 17
        self.assertEqual(late_fee(333, 7), 17)

    # --- validation ---
    def test_reject_negative_amount(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)

    def test_reject_days_out_of_range(self):
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

    def test_reject_str_and_none(self):
        with self.assertRaises(ValueError):
            late_fee('100', 5)
        with self.assertRaises(ValueError):
            late_fee(100, None)


class TestCli(unittest.TestCase):

    def test_cli_ok(self):
        r = run_cli({'amount': 100000, 'days_late': 10})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 7500})

    def test_cli_error(self):
        r = run_cli({'amount': 100000, 'days_late': 400})
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', r.stderr)

    def test_cli_missing_key(self):
        r = run_cli({'amount': 100000})
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
