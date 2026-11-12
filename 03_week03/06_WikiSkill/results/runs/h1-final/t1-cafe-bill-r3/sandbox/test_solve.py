import json
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE_PATH = os.path.join(HERE, "solve.py")


class TestCafeBill(unittest.TestCase):
    # ค่าที่คาดไว้คำนวณด้วยมือ (หน่วยสตางค์)

    def test_normal_no_discount_no_member(self):
        # 300 บาท -> ไม่ลด -> *1.07 = 32100
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 3}], False), 32100)

    def test_bulk_threshold_exact_gets_discount(self):
        # 500 บาทพอดี -> ลด 5% = 47500 -> *1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_just_below_threshold_no_discount(self):
        # 49999 * 1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_threshold_reached_by_sum_of_lines(self):
        # 200 + 150*2 = 500 บาท -> ลด 5% -> 50825
        items = [{"price": 20000, "qty": 1}, {"price": 15000, "qty": 2}]
        self.assertEqual(cafe_bill(items, False), 50825)

    def test_half_up_rounding_at_exact_point_five(self):
        # 50 * 1.07 = 53.5 -> ปัดขึ้นเป็น 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_member_discount_without_bulk(self):
        # 400 บาท -> ไม่ลด -> สมาชิกลด 10% = 36000 -> *1.07 = 38520
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 4}], True), 38520)

    def test_single_rounding_at_end_not_per_step(self):
        # 50001 * 0.95 * 0.9 * 1.07 = 45743.41485 -> 45743
        # (ถ้าปัดทุกขั้นจะได้ 45744 จึงใช้เคสนี้ตรวจการปัดครั้งเดียว)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], True), 45743)

    def test_empty_items_returns_zero(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([], True), 0)

    def test_invalid_inputs_raise_value_error(self):
        ok_item = {"price": 100, "qty": 1}
        bad_cases = [
            ("items not list", ("abc", False)),
            ("item not dict", (["x"], False)),
            ("missing qty", ([{"price": 100}], False)),
            ("extra key", ([{"price": 100, "qty": 1, "x": 1}], False)),
            ("price float", ([{"price": 4500.0, "qty": 1}], False)),
            ("price bool", ([{"price": True, "qty": 1}], False)),
            ("price str", ([{"price": "100", "qty": 1}], False)),
            ("price None", ([{"price": None, "qty": 1}], False)),
            ("price negative", ([{"price": -1, "qty": 1}], False)),
            ("qty zero", ([{"price": 100, "qty": 0}], False)),
            ("qty float", ([{"price": 100, "qty": 1.0}], False)),
            ("qty bool", ([{"price": 100, "qty": False}], False)),
            ("member str", ([ok_item], "yes")),
            ("member int", ([ok_item], 1)),
            ("member None", ([ok_item], None)),
        ]
        for label, (items, member) in bad_cases:
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    cafe_bill(items, member)


class TestCli(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, SOLVE_PATH],
            input=payload,
            capture_output=True,
            text=True,
            cwd=HERE,
        )

    def test_cli_success_exit_0(self):
        payload = json.dumps({"items": [{"price": 10000, "qty": 3}], "member": False})
        proc = self._run(payload)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 32100})

    def test_cli_invalid_value_exit_2(self):
        payload = json.dumps({"items": [{"price": 4500.0, "qty": 1}], "member": False})
        proc = self._run(payload)
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_json_exit_2(self):
        proc = self._run("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_missing_key_exit_2(self):
        proc = self._run(json.dumps({"items": []}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
