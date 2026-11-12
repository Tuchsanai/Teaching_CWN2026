import json
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


class CafeBillTests(unittest.TestCase):
    def test_under_threshold_no_member_adds_vat(self):
        items = [{"price": 3000, "qty": 3}, {"price": 1000, "qty": 2}]
        self.assertEqual(cafe_bill(items, False), 11770)

    def test_exact_threshold_gets_bulk_discount(self):
        items = [{"price": 50000, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 50825)

    def test_just_below_threshold_no_bulk_discount(self):
        items = [{"price": 49950, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 53447)  # ผลก่อนปัดคือ 53446 บวกครึ่ง ปัดขึ้น

    def test_member_discount_under_threshold(self):
        items = [{"price": 10000, "qty": 1}]
        self.assertEqual(cafe_bill(items, True), 9630)

    def test_member_and_bulk_discount_stack(self):
        items = [{"price": 100000, "qty": 1}]
        self.assertEqual(cafe_bill(items, True), 91485)

    def test_half_up_rounding_with_member(self):
        items = [{"price": 500, "qty": 1}]
        self.assertEqual(cafe_bill(items, True), 482)  # 481 บวกครึ่ง ปัดขึ้น

    def test_half_up_rounding_plain(self):
        items = [{"price": 1050, "qty": 1}]
        self.assertEqual(cafe_bill(items, False), 1124)  # 1123 บวกครึ่ง ปัดขึ้น

    def test_empty_items_is_zero(self):
        self.assertEqual(cafe_bill([], True), 0)

    def test_invalid_inputs_raise_value_error(self):
        bad_cases = [
            ("items not list", {"price": 1, "qty": 1}, False),
            ("item not dict", [5], False),
            ("missing qty", [{"price": 100}], False),
            ("qty zero", [{"price": 100, "qty": 0}], False),
            ("qty bool", [{"price": 100, "qty": True}], False),
            ("price string", [{"price": "100", "qty": 1}], False),
            ("price non-int number", [{"price": json.loads("5e0"), "qty": 1}], False),
            ("negative price", [{"price": -1, "qty": 1}], False),
            ("member not bool", [{"price": 100, "qty": 1}], "yes"),
            ("member None", [{"price": 100, "qty": 1}], None),
        ]
        for label, items, member in bad_cases:
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    cafe_bill(items, member)


class CliTests(unittest.TestCase):
    def run_cli(self, stdin_text):
        return subprocess.run(
            [sys.executable, SOLVE],
            input=stdin_text,
            capture_output=True,
            text=True,
        )

    def test_cli_success(self):
        payload = json.dumps({"items": [{"price": 10000, "qty": 1}], "member": True})
        proc = self.run_cli(payload)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 9630})

    def test_cli_invalid_json_exit_2(self):
        proc = self.run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_missing_key_exit_2(self):
        proc = self.run_cli(json.dumps({"items": []}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_value_exit_2(self):
        payload = json.dumps({"items": [{"price": 100, "qty": 0}], "member": False})
        proc = self.run_cli(payload)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
