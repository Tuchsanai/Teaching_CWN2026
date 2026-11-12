import json
import os
import subprocess
import sys
import unittest

from solve import refund

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, 'solve.py')],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestRefund(unittest.TestCase):
    # ค่าปกติ
    def test_basic_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_basic_restock(self):
        # 10000 * 50% = 5000, หัก 12.5% = 625 -> 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_nothing_used_full_refund(self):
        self.assertEqual(refund(10001, 0, False), 10001)

    # ขอบของเงื่อนไข 80%
    def test_exactly_80_percent_still_refunds(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_81_percent_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 81, True), 0)

    def test_100_percent_no_refund(self):
        self.assertEqual(refund(1000, 100, True), 0)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    # ปัดเศษ half-up
    def test_half_up_exact_point_five(self):
        # 4 * 7/8 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_half_up_below_point_five(self):
        # 3 * 7/8 = 2.625 -> 3 ; 2 * 7/8 = 1.75 -> 2 ; 1 * 7/8 = 0.875 -> 1
        self.assertEqual(refund(3, 0, True), 3)
        self.assertEqual(refund(1, 0, True), 1)

    def test_half_up_point_six(self):
        # 10001 * 7/8 = 8750.875 -> 8751
        self.assertEqual(refund(10001, 0, True), 8751)

    def test_half_up_proportional_point_five(self):
        # 5 * (100-50)/100 = 2.5 -> 3
        self.assertEqual(refund(5, 50, False), 3)

    # validation
    def test_reject_negative_paid(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_reject_used_out_of_range(self):
        with self.assertRaises(ValueError):
            refund(100, -1, False)
        with self.assertRaises(ValueError):
            refund(100, 101, False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            refund(100.0, 0, False)
        with self.assertRaises(ValueError):
            refund(100, 50.0, False)

    def test_reject_bool_as_number(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)
        with self.assertRaises(ValueError):
            refund(100, False, False)

    def test_reject_non_bool_restock(self):
        with self.assertRaises(ValueError):
            refund(100, 0, 1)
        with self.assertRaises(ValueError):
            refund(100, 0, None)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            refund('100', 0, False)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        p = run_cli({'paid': 10000, 'used_percent': 50, 'restock': True})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), {'ok': True, 'result': 4375})

    def test_cli_error(self):
        p = run_cli({'paid': 10000, 'used_percent': 150, 'restock': True})
        self.assertEqual(p.returncode, 2)
        out = json.loads(p.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', p.stderr)

    def test_cli_missing_key(self):
        p = run_cli({'paid': 10000, 'used_percent': 50})
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
