import json
import os
import subprocess
import sys
import unittest

from solve import cashback

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, 'solve.py')


def run_cli(payload):
    return subprocess.run(
        [sys.executable, SOLVE],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestCashback(unittest.TestCase):
    # ค่าปกติ (ยอด 100 บาท = 10000 สตางค์)
    def test_normal_values(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)
        self.assertEqual(cashback(10000, 'gold', False), 250)
        self.assertEqual(cashback(10000, 'platinum', False), 400)

    def test_birthday_doubles(self):
        self.assertEqual(cashback(10000, 'silver', True), 300)
        self.assertEqual(cashback(10000, 'gold', True), 500)
        self.assertEqual(cashback(10000, 'platinum', True), 800)

    # ขอบเงื่อนไขขั้นต่ำ 100 บาท
    def test_minimum_boundary(self):
        self.assertEqual(cashback(9999, 'platinum', False), 0)
        self.assertEqual(cashback(9999, 'platinum', True), 0)
        self.assertEqual(cashback(0, 'gold', True), 0)
        self.assertGreater(cashback(10000, 'silver', False), 0)

    # ขอบเพดาน 200 บาท (20000 สตางค์)
    def test_cap_boundary(self):
        # gold 2.5% * 2 เดือนเกิด ที่ 800,000 สตางค์ = 40000 -> ถูกตัดเหลือ 20000
        self.assertEqual(cashback(800000, 'gold', True), 20000)
        # platinum 4% ที่ 500,000 = 20000 พอดีกับเพดาน
        self.assertEqual(cashback(500000, 'platinum', False), 20000)
        self.assertEqual(cashback(500001, 'platinum', False), 20000)
        self.assertEqual(cashback(1000000, 'platinum', True), 20000)

    # half-up: ปัดลงเมื่อเศษ < .5, ปัดขึ้นเมื่อเศษ >= .5
    def test_half_up_exact_point_five(self):
        # gold 2.5%: 10020 * 0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, 'gold', False), 251)
        # silver 1.5%: 10100 * 0.015 = 151.5 -> 152
        self.assertEqual(cashback(10100, 'silver', False), 152)

    def test_half_up_point_six(self):
        # platinum 4%: 10015 * 0.04 = 400.6 -> 401
        self.assertEqual(cashback(10015, 'platinum', False), 401)
        # silver 1.5%: 10040 * 0.015 = 150.6 -> 151
        self.assertEqual(cashback(10040, 'silver', False), 151)

    def test_half_up_below_point_five_rounds_down(self):
        # silver 1.5%: 10033 * 0.015 = 150.495 -> 150
        self.assertEqual(cashback(10033, 'silver', False), 150)

    def test_returns_int(self):
        self.assertIsInstance(cashback(10015, 'platinum', True), int)

    # ValueError: นอกช่วง, float, bool, enum ผิด
    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(-1, 'gold', False)

    def test_float_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, 'gold', False)

    def test_bool_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback(True, 'gold', False)

    def test_str_amount_rejected(self):
        with self.assertRaises(ValueError):
            cashback('10000', 'gold', False)

    def test_bad_tier_rejected(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'bronze', False)
        with self.assertRaises(ValueError):
            cashback(10000, None, False)
        with self.assertRaises(ValueError):
            cashback(10000, 1, False)

    def test_birthday_must_be_bool(self):
        with self.assertRaises(ValueError):
            cashback(10000, 'gold', 1)
        with self.assertRaises(ValueError):
            cashback(10000, 'gold', None)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        r = run_cli({'amount': 10000, 'tier': 'gold', 'birthday': True})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 500})

    def test_cli_error(self):
        r = run_cli({'amount': 10000.0, 'tier': 'gold', 'birthday': False})
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', r.stderr)

    def test_cli_missing_key_error(self):
        r = run_cli({'amount': 10000, 'tier': 'gold'})
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
