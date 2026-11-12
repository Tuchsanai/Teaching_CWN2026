import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def _run_cli(payload):
    return subprocess.run(
        [sys.executable, "solve.py"],
        input=payload,
        capture_output=True,
        text=True,
    )


class TestCafeBill(unittest.TestCase):
    # ค่าคาดคำนวณด้วยมือ (สตางค์)

    def test_normal_no_discount(self):
        # 200 บาท -> ไม่ถึงเกณฑ์, ไม่ใช่สมาชิก: 20000 * 1.07 = 21400
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_multiple_items_summed(self):
        # 3*3000 + 2*1500 = 12000; *1.07 = 12840
        items = [{"price": 3000, "qty": 3}, {"price": 1500, "qty": 2}]
        self.assertEqual(cafe_bill(items, False), 12840)

    def test_threshold_exact_gets_discount(self):
        # 50000 ถึงเกณฑ์พอดี: 50000 * 0.95 = 47500; *1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_just_below_threshold_no_discount(self):
        # 49999 * 1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member_below_threshold(self):
        # 20000 * 0.9 = 18000; *1.07 = 19260
        self.assertEqual(cafe_bill([{"price": 20000, "qty": 1}], True), 19260)

    def test_member_and_threshold_half_up_exact(self):
        # 50000 * 0.95 * 0.9 = 42750; *1.07 = 45742.5 -> 45743 (half up)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_no_intermediate_rounding(self):
        # 50001 * 0.95 * 0.9 * 1.07 = 45743.41485 -> 45743
        # (ถ้าปัดระหว่างทาง จะได้ 45744)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], True), 45743)

    def test_vat_half_up_rounds_up(self):
        # 50 * 1.07 = 53.5 -> 54 (half up, ไม่ใช่ banker's rounding)
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_vat_half_up_rounds_up_again(self):
        # 150 * 1.07 = 160.5 -> 161
        self.assertEqual(cafe_bill([{"price": 150, "qty": 1}], False), 161)

    def test_empty_items_returns_zero(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_rejects_float_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 4500.0, "qty": 1}], False)

    def test_rejects_bool_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_rejects_str_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": "4500", "qty": 1}], False)

    def test_rejects_none_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": None, "qty": 1}], False)

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": -1, "qty": 1}], False)

    def test_rejects_qty_zero(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 0}], False)

    def test_rejects_float_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1.0}], False)

    def test_rejects_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": "2"}], False)

    def test_rejects_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)

    def test_rejects_items_not_list(self):
        with self.assertRaises(ValueError):
            cafe_bill({"price": 100, "qty": 1}, False)

    def test_rejects_item_not_dict(self):
        with self.assertRaises(ValueError):
            cafe_bill([100], False)

    def test_rejects_member_int(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], 1)

    def test_rejects_member_none(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": 1}], None)


class TestCli(unittest.TestCase):

    def test_cli_ok(self):
        r = _run_cli(json.dumps({"items": [{"price": 10000, "qty": 2}], "member": False}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout.strip()), {"ok": True, "result": 21400})

    def test_cli_error_exit_2(self):
        r = _run_cli(json.dumps({"items": [{"price": 4500.0, "qty": 1}], "member": False}))
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout.strip())
        self.assertFalse(out["ok"])
        self.assertIn("error", out)

    def test_cli_bad_json_exit_2(self):
        r = _run_cli("{not json")
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout.strip())["ok"])


if __name__ == "__main__":
    unittest.main()
