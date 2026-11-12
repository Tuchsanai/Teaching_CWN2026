import json
import os
import subprocess
import sys
import unittest

from solve import bulk_price

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, 'solve.py')],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestBulkPrice(unittest.TestCase):
    def test_basic_no_discount(self):
        # 100 บาท x 1 ถุง -> VAT 7% = 107 บาท
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_bulk_3_5_percent(self):
        # 1000 x 10 = 10000 -> -3.5% = 9650 -> VAT = 10325.5 -> half-up 10326
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_bulk_7_5_percent(self):
        # 500000 -> -7.5% = 462500 -> VAT = 494875 (ไม่มีเศษ)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon_stacks_after_bulk(self):
        # 10000 -> -2.5% = 9750 -> VAT = 10432.5 -> half-up 10433
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_tier_boundaries(self):
        # 9 ถุง ยังไม่ลด, 10 ถุงเริ่มลด 3.5%
        self.assertEqual(bulk_price(1000, 9, False), 9630)   # 9000*1.07
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        # 49 ถุงใช้ 3.5%, 50 ถุงใช้ 7.5% (อัตราเดียว ไม่ซ้อนกัน)
        # 49000 -> -3.5% = 47285 -> VAT = 50594.95 -> 50595
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        # 50000 -> -7.5% = 46250 -> VAT = 49487.5 -> 49488
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_half_up_not_floor(self):
        # 10325.5 ต้องปัดขึ้นเป็น 10326 ไม่ใช่ 10325
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_zero_price_is_valid(self):
        self.assertEqual(bulk_price(0, 1, True), 0)

    def test_no_float_drift_large_qty(self):
        # 1000 ถุง ราคา 99999 สตางค์ ต้องเป็นจำนวนเต็มที่ตรงกับการคำนวณ Fraction
        from fractions import Fraction
        exact = Fraction(99999 * 1000) * Fraction(925, 1000) * Fraction(975, 1000) * Fraction(107, 100)
        expected = (2 * exact.numerator + exact.denominator) // (2 * exact.denominator)
        result = bulk_price(99999, 1000, True)
        self.assertIsInstance(result, int)
        self.assertEqual(result, expected)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1.0, False)

    def test_reject_bool_as_int(self):
        with self.assertRaises(ValueError):
            bulk_price(100, True, False)

    def test_reject_non_bool_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 'yes')
        with self.assertRaises(ValueError):
            bulk_price(100, 1, None)

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_reject_str_and_none(self):
        with self.assertRaises(ValueError):
            bulk_price('100', 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, None, False)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        p = run_cli({'unit_price': 10000, 'qty': 1, 'coupon': False})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), {'ok': True, 'result': 10700})

    def test_cli_error(self):
        p = run_cli({'unit_price': 100.0, 'qty': 1, 'coupon': False})
        self.assertEqual(p.returncode, 2)
        out = json.loads(p.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', p.stderr)

    def test_cli_missing_key(self):
        p = run_cli({'unit_price': 100, 'qty': 1})
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
