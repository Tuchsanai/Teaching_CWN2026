import json
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestCafeBill(unittest.TestCase):
    # ---- ค่าปกติ ----
    def test_basic_no_discount_no_member(self):
        # 100 บาท -> ไม่ลด -> +VAT 7% = 107 บาท
        self.assertEqual(cafe_bill([{'price': 10000, 'qty': 1}], False), 10700)

    def test_multiple_items_sum(self):
        # 2 x 150 บาท + 1 x 200 บาท = 500 บาท (ถึงเกณฑ์ลด 5%)
        items = [{'price': 15000, 'qty': 2}, {'price': 20000, 'qty': 1}]
        # 50000 * 0.95 * 1.07 = 50825
        self.assertEqual(cafe_bill(items, False), 50825)

    # ---- ขอบเกณฑ์ 500 บาท ----
    def test_discount_threshold_exact(self):
        # 500 บาทพอดี -> ลด 5%
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], False), 50825)

    def test_below_threshold_no_discount(self):
        # 499.99 บาท -> ไม่ลด: 49999 * 1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{'price': 49999, 'qty': 1}], False), 53499)

    # ---- สมาชิก ----
    def test_member_only_discount_stacks(self):
        # 100 บาท สมาชิก: 10000 * 0.9 * 1.07 = 9630 (ไม่ถึงเกณฑ์ ไม่ลด 5%)
        self.assertEqual(cafe_bill([{'price': 10000, 'qty': 1}], True), 9630)

    def test_member_and_threshold_stack(self):
        # 500 บาท สมาชิก: 50000 * 0.95 * 0.9 * 1.07 = 45742.5 -> 45743 (half-up)
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], True), 45743)

    # ---- ปัดเศษ half-up ----
    def test_half_point_rounds_up(self):
        # 45742.5 -> 45743 (ยืนยันว่าปัดขึ้นที่ .5 พอดี)
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], True), 45743)

    def test_point_six_rounds_up(self):
        # 3 satang, สมาชิก: 3 * 0.9 * 1.07 = 2.889 -> 3
        self.assertEqual(cafe_bill([{'price': 3, 'qty': 1}], True), 3)

    def test_small_amount_not_zero(self):
        # 1 satang, สมาชิก: 1 * 0.9 * 1.07 = 0.963 -> 1 (ไม่ใช่ 0)
        self.assertEqual(cafe_bill([{'price': 1, 'qty': 1}], True), 1)

    def test_no_float_drift(self):
        # 0.1 + 0.2 แบบ float จะเพี้ยน ต้องได้ค่าคงที่
        items = [{'price': 1, 'qty': 1}, {'price': 2, 'qty': 1}]
        # 3 * 1.07 = 3.21 -> 3
        self.assertEqual(cafe_bill(items, False), 3)

    # ---- ValueError ----
    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000, 'qty': 0}], False)

    def test_qty_negative_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000, 'qty': -1}], False)

    def test_price_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100.0, 'qty': 1}], False)

    def test_qty_string_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000, 'qty': '1'}], False)

    def test_qty_bool_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000, 'qty': True}], False)

    def test_member_not_bool_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000, 'qty': 1}], 1)

    def test_member_none_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000, 'qty': 1}], None)

    def test_items_not_list_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill({'price': 1000, 'qty': 1}, False)

    def test_items_empty_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([], False)

    def test_item_not_dict_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([1000], False)

    def test_item_missing_key_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1000}], False)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        r = run_cli({'items': [{'price': 10000, 'qty': 1}], 'member': False})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 10700})

    def test_cli_error(self):
        r = run_cli({'items': [{'price': 10000, 'qty': 0}], 'member': False})
        self.assertEqual(r.returncode, 2, r.stderr)
        out = json.loads(r.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', r.stderr)

    def test_cli_missing_key_error(self):
        r = run_cli({'items': [{'price': 10000, 'qty': 1}]})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertFalse(json.loads(r.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
