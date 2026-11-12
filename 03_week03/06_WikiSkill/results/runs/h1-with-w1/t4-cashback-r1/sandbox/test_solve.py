import json
import os
import subprocess
import sys
import unittest

from solve import cashback

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, 'solve.py')],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestCashback(unittest.TestCase):
    # ---- ค่าปกติ ----
    def test_basic_silver(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_basic_gold(self):
        self.assertEqual(cashback(20000, 'gold', False), 500)

    def test_basic_platinum(self):
        self.assertEqual(cashback(20000, 'platinum', False), 800)

    def test_birthday_doubles(self):
        self.assertEqual(cashback(20000, 'gold', True), 1000)

    # ---- ขอบเขตขั้นต่ำ 100 บาท ----
    def test_below_min_no_cashback(self):
        self.assertEqual(cashback(9999, 'platinum', True), 0)

    def test_exact_min_gets_cashback(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, 'gold', True), 0)

    # ---- เพดาน 200 บาท ----
    def test_cap_exact(self):
        self.assertEqual(cashback(500000, 'platinum', False), 20000)

    def test_cap_applies_non_birthday(self):
        self.assertEqual(cashback(600000, 'platinum', False), 20000)

    def test_cap_applies_after_birthday_doubling(self):
        self.assertEqual(cashback(400000, 'gold', True), 20000)
        self.assertEqual(cashback(500000, 'gold', True), 20000)

    def test_near_cap_rounding(self):
        # 4% ของ 499,999 = 19,999.96 -> ปัดครึ่งขึ้นได้ 20000 (เท่ากับเพดานพอดี)
        self.assertEqual(cashback(499999, 'platinum', False), 20000)
        # 4% ของ 490,000 = 19,600 พอดี (ต่ำกว่าเพดาน ไม่ถูกตัด)
        self.assertEqual(cashback(490000, 'platinum', False), 19600)

    # ---- half-up ----
    def test_half_up_silver_point5(self):
        # 10100 * 1.5% = 151.5 -> 152
        self.assertEqual(cashback(10100, 'silver', False), 152)

    def test_half_up_gold_point5(self):
        # 10020 * 2.5% = 250.5 -> 251
        self.assertEqual(cashback(10020, 'gold', False), 251)

    def test_half_up_point6_rounds_up(self):
        # 10040 * 1.5% = 150.6 -> 151
        self.assertEqual(cashback(10040, 'silver', False), 151)

    def test_half_up_point4_rounds_down(self):
        # 10160 * 1.5% = 152.4 -> 152
        self.assertEqual(cashback(10160, 'silver', False), 152)

    # ---- ValueError ----
    def test_reject_float_amount(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, 'silver', False)

    def test_reject_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, 'silver', False)

    def test_reject_negative_amount(self):
        with self.assertRaises(ValueError):
            cashback(-1, 'silver', False)

    def test_reject_str_amount(self):
        with self.assertRaises(ValueError):
            cashback('10000', 'silver', False)

    def test_reject_bad_tier(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'bronze', False)

    def test_reject_tier_case_sensitive(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'Gold', False)

    def test_reject_tier_none(self):
        with self.assertRaises(ValueError):
            cashback(10000, None, False)

    def test_reject_non_bool_birthday(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'silver', 1)

    def test_reject_none_birthday(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'silver', None)

    # ---- CLI ----
    def test_cli_ok(self):
        r = run_cli({'amount': 10100, 'tier': 'silver', 'birthday': False})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 152})

    def test_cli_error(self):
        r = run_cli({'amount': 10.5, 'tier': 'silver', 'birthday': False})
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', r.stderr)


if __name__ == '__main__':
    unittest.main()
