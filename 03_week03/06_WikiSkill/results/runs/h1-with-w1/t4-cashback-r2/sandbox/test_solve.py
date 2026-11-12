import json
import os
import subprocess
import sys
import unittest

from solve import cashback

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload_text):
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=payload_text,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestCashback(unittest.TestCase):
    # ค่าปกติ
    def test_gold_normal(self):
        self.assertEqual(cashback(20000, 'gold', False), 500)

    def test_silver_normal(self):
        self.assertEqual(cashback(20000, 'silver', False), 300)

    def test_platinum_normal(self):
        self.assertEqual(cashback(20000, 'platinum', False), 800)

    # ขอบเงื่อนไขขั้นต่ำ 100 บาท
    def test_below_minimum_no_cashback(self):
        self.assertEqual(cashback(9999, 'platinum', True), 0)

    def test_exact_minimum_gets_cashback(self):
        self.assertEqual(cashback(10000, 'gold', False), 250)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, 'gold', True), 0)

    # half-up: 2.5% ของ 10020 = 250.5 -> 251
    def test_half_up_gold(self):
        self.assertEqual(cashback(10020, 'gold', False), 251)

    # half-up: 1.5% ของ 10100 = 151.5 -> 152
    def test_half_up_silver(self):
        self.assertEqual(cashback(10100, 'silver', False), 152)

    # ไม่ถึงครึ่ง ปัดลง: 1.5% ของ 10033 = 150.495 -> 150
    def test_round_down_below_half(self):
        self.assertEqual(cashback(10033, 'silver', False), 150)

    # 4% ของ 10013 = 400.52 -> 401
    def test_round_up_above_half(self):
        self.assertEqual(cashback(10013, 'platinum', False), 401)

    # เดือนเกิด 2 เท่า
    def test_birthday_doubles(self):
        self.assertEqual(cashback(10000, 'gold', True), 500)

    def test_birthday_below_minimum_still_zero(self):
        self.assertEqual(cashback(9000, 'platinum', True), 0)

    # เพดาน 200 บาท
    def test_cap_exact_boundary(self):
        self.assertEqual(cashback(500000, 'platinum', False), 20000)

    def test_cap_applies_above_boundary(self):
        self.assertEqual(cashback(1000000, 'gold', False), 20000)

    def test_cap_with_birthday(self):
        self.assertEqual(cashback(500000, 'platinum', True), 20000)

    def test_below_cap_not_capped(self):
        self.assertEqual(cashback(1000000, 'silver', False), 15000)

    # ValueError
    def test_amount_negative(self):
        with self.assertRaises(ValueError):
            cashback(-1, 'gold', False)

    def test_amount_float(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, 'gold', False)

    def test_amount_str(self):
        with self.assertRaises(ValueError):
            cashback('10000', 'gold', False)

    def test_amount_none(self):
        with self.assertRaises(ValueError):
            cashback(None, 'gold', False)

    def test_amount_bool(self):
        with self.assertRaises(ValueError):
            cashback(True, 'gold', False)

    def test_tier_invalid(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'bronze', False)

    def test_tier_not_str(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_birthday_not_bool(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'gold', 1)

    def test_birthday_none(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'gold', None)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        payload = json.dumps({'amount': 20000, 'tier': 'gold', 'birthday': False})
        proc = run_cli(payload)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 500})

    def test_cli_error(self):
        payload = json.dumps({'amount': 20000.0, 'tier': 'gold', 'birthday': False})
        proc = run_cli(payload)
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli(json.dumps({'amount': 20000, 'tier': 'gold'}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])

    def test_cli_bad_json(self):
        proc = run_cli('{not json')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
