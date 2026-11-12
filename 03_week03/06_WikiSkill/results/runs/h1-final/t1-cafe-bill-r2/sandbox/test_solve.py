import json
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    if isinstance(payload, str):
        stdin_text = payload
    else:
        stdin_text = json.dumps(payload)
    return subprocess.run(
        [sys.executable, os.path.join(HERE, "solve.py")],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestCafeBill(unittest.TestCase):
    # ค่าคาดทั้งหมดคำนวณด้วยมือ (หน่วยสตางค์) แยกจากโค้ด

    def test_basic_no_discount_no_member(self):
        # 100 บาท -> x 1.07 = 107 บาท = 10700 สตางค์
        items = [{"price": 10000, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 10700)

    def test_multiple_items_and_qty(self):
        # 2 x 3000 + 1 x 4500 = 10500 -> x 1.07 = 11235
        items = [{"price": 3000, "qty": 2}, {"price": 4500, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 11235)

    def test_empty_items_is_zero(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)

    def test_threshold_just_below_no_discount(self):
        # 49999 x 1.07 = 53498.93 -> half up 53499
        items = [{"price": 49999, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 53499)

    def test_threshold_exact_gets_5_percent(self):
        # 50000 x 0.95 = 47500 x 1.07 = 50825 (ไม่มีเศษ)
        items = [{"price": 50000, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 50825)

    def test_threshold_just_above(self):
        # 50001 x 0.95 = 47500.95 x 1.07 = 50826.0165 -> 50826
        items = [{"price": 50001, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 50826)

    def test_threshold_checked_on_subtotal_across_items(self):
        # แต่ละชิ้นไม่ถึง 500 แต่รวมกันถึง -> ได้ส่วนลด 5%
        # 30000 + 20000 = 50000 -> 50825
        items = [{"price": 30000, "qty": 1}, {"price": 10000, "qty": 2}]
        self.assertEqual(cafe_bill(items, False), 50825)

    def test_half_up_rounding_at_vat(self):
        # 50 x 1.07 = 53.5 -> half up 54 (floor จะได้ 53)
        items = [{"price": 50, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 54)

    def test_member_discount_applied_multiplicatively(self):
        # 50000 x 0.95 x 0.90 = 42750 x 1.07 = 45742.5 -> half up 45743
        items = [{"price": 50000, "qty": 1}]
        self.assertEqual(cafe_bill(items, True), 45743)

    def test_member_below_threshold(self):
        # 10000 x 0.90 = 9000 x 1.07 = 9630
        items = [{"price": 10000, "qty": 1}]
        self.assertEqual(cafe_bill(items, True), 9630)

    def test_single_rounding_at_end(self):
        # 10100 x 0.90 = 9090 x 1.07 = 9726.3 -> 9726
        # (ถ้าปัดขั้นกลางเป็น 9090 -> 9726.3 เหมือนกัน แต่เคสนี้ยืนยันว่าไม่มีการปัดก่อน VAT)
        items = [{"price": 10100, "qty": 1}]
        self.assertEqual(cafe_bill(items, True), 9726)

    def test_single_rounding_multi_step_half_case(self):
        # 2 x 25 = 50 -> member: 50 x 0.90 = 45 -> x 1.07 = 48.15 -> 48
        # (ถ้าปัดเป็นจำนวนเต็มที่ขั้นกลางจะได้ผลต่างกันในบางกรณี)
        items = [{"price": 25, "qty": 2}]
        self.assertEqual(cafe_bill(items, True), 48)

    def test_result_is_int(self):
        result = cafe_bill([{"price": 100, "qty": 3}], True)
        self.assertIsInstance(result, int)
        self.assertNotIsInstance(result, bool)

    # ---- validation: ทุกกรณีต้อง raise ValueError ----

    def test_items_not_list(self):
        with self.assertRaises(ValueError):
            cafe_bill({"price": 100, "qty": 1}, False)
        with self.assertRaises(ValueError):
            cafe_bill(None, False)
        with self.assertRaises(ValueError):
            cafe_bill("abc", False)

    def test_item_not_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([[100, 1]], False)
        with self.assertRaises(ValueError):
            cafe_bill([None], False)

    def test_item_missing_keys(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)
        with self.assertRaises(ValueError):
            cafe_bill([{"qty": 1}], False)

    def test_price_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500.0, "qty": 1}], False)

    def test_price_bool_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_price_str_none_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": "100", "qty": 1}], False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": None, "qty": 1}], False)

    def test_price_negative_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": -1, "qty": 1}], False)

    def test_qty_zero_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 0}], False)

    def test_qty_float_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1.0}], False)

    def test_qty_bool_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": True}], False)

    def test_qty_str_rejected(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": "1"}], False)

    def test_member_must_be_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], 1)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], 0)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], "yes")
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], None)

    # ---- CLI: stdin JSON ----

    def test_cli_success(self):
        proc = run_cli({"items": [{"price": 10000, "qty": 1}], "member": False})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 10700})

    def test_cli_success_member(self):
        proc = run_cli({"items": [{"price": 50000, "qty": 1}], "member": True})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 45743})

    def test_cli_invalid_value_exit_2(self):
        proc = run_cli({"items": [{"price": 4500.0, "qty": 1}], "member": False})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertIn("error", out)
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_missing_key_exit_2(self):
        proc = run_cli({"items": [{"price": 100, "qty": 1}]})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_extra_key_exit_2(self):
        proc = run_cli({"items": [], "member": False, "extra": 1})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_bad_json_exit_2(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_non_object_exit_2(self):
        proc = run_cli("[1, 2, 3]")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
