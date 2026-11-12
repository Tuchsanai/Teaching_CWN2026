import json
import os
import subprocess
import sys
import unittest

from solve import bulk_price

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, 'solve.py')


def run_cli(payload):
    return subprocess.run(
        [sys.executable, SOLVE],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestBulkPrice(unittest.TestCase):
    # ค่าปกติ
    def test_single_bag_no_coupon(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_tier_3_5_percent(self):
        # 100000 * 0.965 * 1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier_7_5_percent(self):
        # 500000 * 0.925 * 1.07 = 494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon_sequential_discount(self):
        # ลดคูปองหลังส่วนลดจำนวน: 50000 * 0.925 * 0.975 * 1.07 = 48250.3125 -> 48250
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    # ขอบของเงื่อนไขจำนวนถุง
    def test_boundary_qty_9_no_discount(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_boundary_qty_10_has_discount(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_boundary_qty_49_still_3_5(self):
        # 490000 * 0.965 * 1.07 = 505949.5 -> 505950 (half-up)
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_boundary_qty_50_has_7_5(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_boundary_qty_1000(self):
        # 10000000 * 0.925 * 1.07 = 9897500
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)

    # การปัดเศษ half-up
    def test_half_up_at_exact_point_5(self):
        # 10000 * 0.975 * 1.07 = 10432.5 -> 10433
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_below_point_5_rounds_down(self):
        # 1 * 1.07 = 1.07 -> 1
        self.assertEqual(bulk_price(1, 1, False), 1)

    # Validation
    def test_reject_negative_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_reject_float_price(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)

    def test_reject_str_price(self):
        with self.assertRaises(ValueError):
            bulk_price('100', 1, False)

    def test_reject_none_price(self):
        with self.assertRaises(ValueError):
            bulk_price(None, 1, False)

    def test_reject_bool_price(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)

    def test_reject_qty_zero(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)

    def test_reject_qty_1001(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_reject_qty_float(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 10.0, False)

    def test_reject_qty_bool(self):
        with self.assertRaises(ValueError):
            bulk_price(100, True, False)

    def test_reject_coupon_int(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)

    def test_reject_coupon_str(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 'yes')


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli({'unit_price': 10000, 'qty': 10, 'coupon': False})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 103255})

    def test_cli_error(self):
        proc = run_cli({'unit_price': 10000, 'qty': 0, 'coupon': False})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli({'unit_price': 10000, 'qty': 10})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
