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
        # 24,000 * 1.07 = 25,680
        self.assertEqual(cafe_bill([{'price': 12000, 'qty': 2}], False), 25680)

    def test_multiple_items_summed(self):
        items = [{'price': 3500, 'qty': 2}, {'price': 4500, 'qty': 1}]
        # 11,500 * 1.07 = 12,305
        self.assertEqual(cafe_bill(items, False), 12305)

    def test_threshold_below_500_baht_no_discount(self):
        # 49,999 * 1.07 = 53,498.93 -> 53,499
        self.assertEqual(cafe_bill([{'price': 49999, 'qty': 1}], False), 53499)

    def test_threshold_exact_500_baht_gets_discount(self):
        # 50,000 * 0.95 * 1.07 = 50,825
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], False), 50825)

    def test_member_stacks_after_discount(self):
        # 50,000 * 0.95 * 0.90 * 1.07 = 45,742.5 -> 45,743 (half-up)
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], True), 45743)

    def test_member_below_threshold(self):
        # 10,000 * 0.90 * 1.07 = 9,630
        self.assertEqual(cafe_bill([{'price': 10000, 'qty': 1}], True), 9630)

    def test_half_up_at_point_five(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{'price': 50, 'qty': 1}], False), 54)

    def test_half_up_at_point_six(self):
        # 80 * 1.07 = 85.6 -> 86
        self.assertEqual(cafe_bill([{'price': 80, 'qty': 1}], False), 86)

    def test_round_down_at_point_four(self):
        # 20 * 1.07 = 21.4 -> 21
        self.assertEqual(cafe_bill([{'price': 20, 'qty': 1}], False), 21)

    def test_no_drift_small_amount(self):
        # 1 สตางค์ * 1.07 = 1.07 -> 1 (ไม่ปัดกลางทางจนเพี้ยน)
        self.assertEqual(cafe_bill([{'price': 1, 'qty': 1}], False), 1)

    def test_no_drift_multi_step_single_round(self):
        # 50,000 * 0.95 * 0.90 * 1.07 = 45,742.5 -> 45,743 ปัดครั้งเดียวตอนท้าย
        self.assertEqual(cafe_bill([{'price': 25000, 'qty': 2}], True), 45743)

    def test_rejects_empty_items(self):
        with self.assertRaises(ValueError):
            cafe_bill([], False)

    def test_rejects_items_not_list(self):
        with self.assertRaises(ValueError):
            cafe_bill({'price': 100, 'qty': 1}, False)

    def test_rejects_item_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100}], False)

    def test_rejects_item_not_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([100], False)

    def test_rejects_float_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100.0, 'qty': 1}], False)

    def test_rejects_bool_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': True, 'qty': 1}], False)

    def test_rejects_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': '1'}], False)

    def test_rejects_zero_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': 0}], False)

    def test_rejects_negative_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': -1}], False)

    def test_rejects_zero_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 0, 'qty': 1}], False)

    def test_rejects_non_bool_member(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': 1}], 'yes')

    def test_rejects_int_member(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 100, 'qty': 1}], 1)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        r = run_cli({'items': [{'price': 50000, 'qty': 1}], 'member': True})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 45743})

    def test_cli_error(self):
        r = run_cli({'items': [{'price': 100.0, 'qty': 1}], 'member': False})
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', r.stderr)

    def test_cli_missing_key(self):
        r = run_cli({'items': [{'price': 100, 'qty': 1}]})
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
