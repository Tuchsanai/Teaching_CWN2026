import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    def test_normal_no_restock(self):
        self.assertEqual(refund(1000, 0, False), 1000)
        self.assertEqual(refund(1000, 50, False), 500)

    def test_normal_with_restock_fee(self):
        # 1000 * 7/8 = 875 (ไม่มีเศษ)
        self.assertEqual(refund(1000, 0, True), 875)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(0, 50, False), 0)

    def test_boundary_80_refunds(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 80, True), 175)

    def test_boundary_81_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 81, True), 0)

    def test_boundary_100_no_refund(self):
        self.assertEqual(refund(1000, 100, False), 0)

    def test_half_up_exact_point_five(self):
        # 100 * 7/8 = 87.5 -> 88 (half-up)
        self.assertEqual(refund(100, 0, True), 88)
        # 3 * 50/100 = 1.5 -> 2
        self.assertEqual(refund(3, 50, False), 2)

    def test_half_up_point_six_and_point_four(self):
        # 1 * 60/100 = 0.6 -> 1
        self.assertEqual(refund(1, 40, False), 1)
        # 3 * 40/100 = 1.2 -> 1 (ปัดลงเมื่อเศษ .2)
        self.assertEqual(refund(3, 60, False), 1)
        # 3 * 60/100 = 1.8 -> 2
        self.assertEqual(refund(3, 40, False), 2)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            refund(1000.0, 0, False)
        with self.assertRaises(ValueError):
            refund(1000, 50.0, False)

    def test_reject_bool_as_int(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)
        with self.assertRaises(ValueError):
            refund(1000, False, False)

    def test_reject_string_and_none(self):
        with self.assertRaises(ValueError):
            refund('1000', 0, False)
        with self.assertRaises(ValueError):
            refund(None, 0, False)

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)
        with self.assertRaises(ValueError):
            refund(1000, -1, False)
        with self.assertRaises(ValueError):
            refund(1000, 101, False)

    def test_reject_non_bool_restock(self):
        with self.assertRaises(ValueError):
            refund(1000, 0, 1)
        with self.assertRaises(ValueError):
            refund(1000, 0, None)


class TestCli(unittest.TestCase):
    def run_cli(self, payload):
        return subprocess.run(
            [sys.executable, 'solve.py'],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        proc = self.run_cli({'paid': 1000, 'used_percent': 0, 'restock': True})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 875})

    def test_cli_error(self):
        proc = self.run_cli({'paid': 1000.0, 'used_percent': 0, 'restock': False})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = self.run_cli({'paid': 1000, 'used_percent': 0})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
