import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    # ค่าปกติ
    def test_normal(self):
        # 1000 สต. * 0.75% * 4 วัน = 30
        self.assertEqual(late_fee(1000, 4), 30)
        # 1000 * 0.75% * 10 = 75
        self.assertEqual(late_fee(1000, 10), 75)

    # ขอบของเงื่อนไขช้าไม่เกิน 3 วัน
    def test_grace_boundary(self):
        self.assertEqual(late_fee(1000, 0), 0)
        self.assertEqual(late_fee(1000, 3), 0)   # พอดี 3 วัน ไม่คิด
        self.assertEqual(late_fee(1000, 4), 30)  # 4 วัน เริ่มคิด (นับทั้ง 4 วัน)

    # ขอบเพดาน 15%
    def test_cap_boundary(self):
        # 20 วัน * 0.75% = 15% พอดี
        self.assertEqual(late_fee(1000, 20), 150)
        # 21 วัน จะเกิน 15% แต่ต้องถูกตัดที่เพดาน
        self.assertEqual(late_fee(1000, 21), 150)
        self.assertEqual(late_fee(1000, 365), 150)

    def test_cap_applied_before_rounding(self):
        # 1 สต. * 15% = 0.15 -> 0 (เพดานไม่ทำให้ค่าเพิ่มขึ้น)
        self.assertEqual(late_fee(1, 365), 0)

    # half-up: 150 * 0.75% * 4 = 4.5 -> 5 (banker's rounding จะได้ 4)
    def test_half_up_at_point_five(self):
        self.assertEqual(late_fee(150, 4), 5)

    # half-up: 20 * 0.75% * 4 = 0.6 -> 1
    def test_half_up_above_point_five(self):
        self.assertEqual(late_fee(20, 4), 1)

    # ปัดลงเมื่อต่ำกว่า .5: 10 * 0.75% * 4 = 0.3 -> 0
    def test_round_down_below_point_five(self):
        self.assertEqual(late_fee(10, 4), 0)

    def test_returns_int(self):
        self.assertIsInstance(late_fee(1000, 4), int)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)

    # validation
    def test_reject_out_of_range_days(self):
        with self.assertRaises(ValueError):
            late_fee(1000, -1)
        with self.assertRaises(ValueError):
            late_fee(1000, 366)

    def test_reject_negative_amount(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            late_fee(1000.0, 5)
        with self.assertRaises(ValueError):
            late_fee(1000, 5.0)

    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            late_fee(True, 5)
        with self.assertRaises(ValueError):
            late_fee(1000, False)

    def test_reject_str_and_none(self):
        with self.assertRaises(ValueError):
            late_fee('1000', 5)
        with self.assertRaises(ValueError):
            late_fee(None, 5)


class TestCli(unittest.TestCase):
    def run_cli(self, payload):
        return subprocess.run(
            [sys.executable, 'solve.py'],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        proc = self.run_cli(json.dumps({'amount': 1000, 'days_late': 4}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 30})

    def test_cli_error(self):
        proc = self.run_cli(json.dumps({'amount': 1000, 'days_late': 400}))
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = self.run_cli(json.dumps({'amount': 1000}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
