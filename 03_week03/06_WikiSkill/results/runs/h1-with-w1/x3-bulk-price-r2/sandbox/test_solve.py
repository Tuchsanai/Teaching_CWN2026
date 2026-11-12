import json
import os
import subprocess
import sys
import unittest

from solve import bulk_price

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestBulkPrice(unittest.TestCase):
    def test_normal_no_discount_no_coupon(self):
        # 10000 × 1 × 1.07 = 10700
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_tier_10_with_coupon(self):
        # 50000 × 0.965 × 0.975 × 1.07 = 50336.8125 → 50337
        self.assertEqual(bulk_price(5000, 10, True), 50337)

    def test_normal_tier_50_with_coupon(self):
        # 50000 × 0.925 × 0.975 × 1.07 = 48250.3125 → 48250
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_tier_boundary_9_no_discount(self):
        # 9000 × 1.07 = 9630
        self.assertEqual(bulk_price(1000, 9, False), 9630)

    def test_tier_boundary_10_discount_starts(self):
        # 10000 × 0.965 × 1.07 = 10325.5 → 10326
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_tier_boundary_49_still_3_5_percent(self):
        # 49000 × 0.965 × 1.07 = 50594.95 → 50595
        self.assertEqual(bulk_price(1000, 49, False), 50595)

    def test_tier_boundary_50_discount_7_5_percent(self):
        # 50000 × 0.925 × 1.07 = 49487.5 → 49488
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_coupon_on_tier_0(self):
        # 9000 × 0.975 × 1.07 = 9389.25 → 9389
        self.assertEqual(bulk_price(1000, 9, True), 9389)

    def test_coupon_is_cheaper(self):
        self.assertLess(bulk_price(1000, 1, True), bulk_price(1000, 1, False))

    def test_half_up_at_exact_half(self):
        # 10000 × 0.965 × 1.07 = 10325.5 exactly → half-up gives 10326 (not 10325)
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_half_up_small_amount(self):
        # 1000 × 0.965 × 1.07 = 1032.55 → 1033
        self.assertEqual(bulk_price(100, 10, False), 1033)

    def test_zero_price_allowed(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_result_is_int(self):
        self.assertIsInstance(bulk_price(1234, 77, True), int)

    def test_reject_float_price(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)

    def test_reject_negative_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_reject_bool_price(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)

    def test_reject_qty_out_of_range(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_reject_qty_float_or_str(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 10.0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, '10', False)

    def test_reject_coupon_not_bool(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 'yes')
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)

    def test_reject_none(self):
        with self.assertRaises(ValueError):
            bulk_price(None, 1, False)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli({'unit_price': 1000, 'qty': 10, 'coupon': False})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 10326})

    def test_cli_error(self):
        proc = run_cli({'unit_price': 1000, 'qty': 0, 'coupon': False})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli({'unit_price': 1000, 'qty': 1})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
