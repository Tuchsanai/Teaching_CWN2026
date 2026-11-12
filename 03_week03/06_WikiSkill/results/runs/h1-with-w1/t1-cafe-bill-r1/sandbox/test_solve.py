import json
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, 'solve.py')],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestCafeBill(unittest.TestCase):
    def test_basic_no_discount_no_member(self):
        # 100 บาท -> +VAT 7% = 107 บาท
        self.assertEqual(cafe_bill([{'price': 10000, 'qty': 1}], False), 10700)

    def test_multiple_items_sum(self):
        items = [{'price': 2500, 'qty': 2}, {'price': 3000, 'qty': 1}]  # 80 บาท
        self.assertEqual(cafe_bill(items, False), 8560)

    def test_bulk_threshold_boundary(self):
        # 499.99 บาท: ไม่ลด -> 49999 * 1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{'price': 49999, 'qty': 1}], False), 53499)
        # 500 บาทพอดี: ลด 5% -> 47500 * 1.07 = 50825
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], False), 50825)

    def test_member_discount(self):
        # 1000 บาท: ลด 5% -> 950, ลดสมาชิก 10% -> 855, VAT -> 914.85 บาท
        self.assertEqual(cafe_bill([{'price': 100000, 'qty': 1}], True), 91485)

    def test_multiplicative_order(self):
        # ลดแบบต่อกัน (0.95 * 0.90) ไม่ใช่รวมเป็นลด 15%
        # 1000 บาท: ต่อกัน = 91485; ถ้ารวมลด 15% จะได้ 90950
        items = [{'price': 100000, 'qty': 1}]
        self.assertEqual(cafe_bill(items, True), 91485)
        self.assertNotEqual(cafe_bill(items, True), 90950)

    def test_half_up_rounding_at_point_five(self):
        # 50 * 1.07 = 53.5 -> 54 (half-up)
        self.assertEqual(cafe_bill([{'price': 50, 'qty': 1}], False), 54)

    def test_half_up_rounding_above_point_five(self):
        # 51 * 1.07 = 54.57 -> 55 (ไม่ปัดลงเป็น 54)
        self.assertEqual(cafe_bill([{'price': 51, 'qty': 1}], False), 55)

    def test_no_intermediate_rounding_drift(self):
        # subtotal 50000 -> *0.95 = 47500 -> *0.9 = 42750 -> *1.07 = 45742.5 -> 45743
        # ถ้าปัดกลางทางจะได้ค่าต่างออกไป
        items = [{'price': 1, 'qty': 50000}]
        self.assertEqual(cafe_bill(items, True), 45743)

    def test_qty_large_bulk(self):
        # 100000 * 0.95 = 95000 * 1.07 = 101650 (ลด 5% เพราะยอดเกิน 500 บาท)
        self.assertEqual(cafe_bill([{'price': 1000, 'qty': 100}], False), 101650)

    def test_reject_empty_items(self):
        with self.assertRaises(ValueError):
            cafe_bill([], False)

    def test_reject_items_not_list(self):
        with self.assertRaises(ValueError):
            cafe_bill({'price': 100, 'qty': 1}, False)

    def test_reject_item_not_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([100], False)

    def test_reject_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100}], False)

    def test_reject_float_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100.0, 'qty': 1}], False)

    def test_reject_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': '1'}], False)

    def test_reject_none_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': None, 'qty': 1}], False)

    def test_reject_bool_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': True, 'qty': 1}], False)

    def test_reject_zero_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': 0}], False)

    def test_reject_negative_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': -1}], False)

    def test_reject_zero_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 0, 'qty': 1}], False)

    def test_reject_member_not_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': 1}], 1)

    def test_reject_member_none(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': 1}], None)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli({'items': [{'price': 10000, 'qty': 1}], 'member': False})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out, {'ok': True, 'result': 10700})

    def test_cli_error(self):
        proc = run_cli({'items': [{'price': 10000, 'qty': 0}], 'member': False})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli({'items': [{'price': 10000, 'qty': 1}]})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
