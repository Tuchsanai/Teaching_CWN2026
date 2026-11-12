import json
import os
import subprocess
import sys
import unittest

from solve import refund

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestRefundBasic(unittest.TestCase):
    def test_no_use_no_fee(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_half_used_no_fee(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_with_restock_fee(self):
        # คืนตามสัดส่วน 7500 หักค่าดำเนินการ 12.5% = 937.5 -> เหลือ 6562.5 -> 6563
        self.assertEqual(refund(10000, 25, True), 6563)

    def test_zero_paid_is_zero(self):
        self.assertEqual(refund(0, 0, True), 0)


class TestRefundBoundary(unittest.TestCase):
    def test_used_80_still_refunded(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_used_81_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_used_100_no_refund(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_used_0_and_100_accepted_as_range_edges(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 100, False), 0)


class TestRefundRounding(unittest.TestCase):
    def test_exact_half_rounds_up(self):
        # 1 * 50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 4 * 7/8 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)
        # 12 * 7/8 = 10.5 -> 11
        self.assertEqual(refund(12, 0, True), 11)

    def test_below_half_rounds_down(self):
        # 1 * (100-60)/100 = 0.4 -> 0
        self.assertEqual(refund(1, 60, False), 0)
        # 2 * 7/8 = 1.75 -> 2 (ทดสอบว่าไม่ได้ปัดลง)
        self.assertEqual(refund(2, 0, True), 2)
        # 3 * 7/8 = 2.625 -> 3
        self.assertEqual(refund(3, 0, True), 3)

    def test_single_rounding_at_end(self):
        # 10 * (100-33)/100 = 6.7 ; หักค่าดำเนินการ -> 6.7 * 7/8 = 5.8625 -> 6
        self.assertEqual(refund(10, 33, True), 6)


class TestRefundValidation(unittest.TestCase):
    def test_paid_negative_rejected(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_paid_float_rejected(self):
        with self.assertRaises(ValueError):
            refund(100.0, 0, False)

    def test_paid_str_rejected(self):
        with self.assertRaises(ValueError):
            refund('100', 0, False)

    def test_paid_bool_rejected(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)

    def test_used_percent_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            refund(100, -1, False)
        with self.assertRaises(ValueError):
            refund(100, 101, False)

    def test_used_percent_float_rejected(self):
        with self.assertRaises(ValueError):
            refund(100, 50.0, False)

    def test_used_percent_bool_rejected(self):
        with self.assertRaises(ValueError):
            refund(100, False, False)

    def test_restock_must_be_bool(self):
        with self.assertRaises(ValueError):
            refund(100, 0, 1)
        with self.assertRaises(ValueError):
            refund(100, 0, None)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli({'paid': 10000, 'used_percent': 25, 'restock': True})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 6563})

    def test_cli_error(self):
        proc = run_cli({'paid': 10000, 'used_percent': 101, 'restock': True})
        self.assertEqual(proc.returncode, 2, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)


if __name__ == '__main__':
    unittest.main()
