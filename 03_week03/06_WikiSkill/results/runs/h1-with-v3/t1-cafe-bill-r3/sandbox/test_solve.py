import json
import math
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


class CafeBillTest(unittest.TestCase):
    def test_under_threshold_no_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_exact_threshold_gets_bulk_discount(self):
        # 50000 * 0.95 = 47500, * 1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_just_below_threshold_no_bulk_discount(self):
        # 49999 * 1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member_only(self):
        # 10000 * 0.9 = 9000, * 1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_bulk_and_member_discounts_compound(self):
        # 100000 * 0.95 = 95000, * 0.9 = 85500, * 1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 100000, "qty": 1}], True), 91485)

    def test_multiple_items_with_qty(self):
        items = [{"price": 1500, "qty": 20}, {"price": 2500, "qty": 2}]
        # subtotal 35000, * 0.9 = 31500, * 1.07 = 33705
        self.assertEqual(cafe_bill(items, True), 33705)

    def test_half_up_rounding(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_round_down_below_half(self):
        # 1 * 1.07 = 1.07 -> 1
        self.assertEqual(cafe_bill([{"price": 1, "qty": 1}], False), 1)

    def test_invalid_inputs_raise_value_error(self):
        bad_cases = [
            ([{"price": math.sqrt(25), "qty": 1}], False),  # float price
            ([{"price": 100, "qty": 0}], False),            # qty below 1
            ([{"price": True, "qty": 1}], False),           # bool is not int
            ([{"price": 100, "qty": 1}], "yes"),            # member not bool
            ([{"price": 100, "qty": 1}], None),
            ([], False),                                    # empty bill
            ("not a list", False),
            ([{"price": 100}], False),                      # missing qty
        ]
        for items, member in bad_cases:
            with self.subTest(items=items, member=member):
                with self.assertRaises(ValueError):
                    cafe_bill(items, member)

    def test_cli_success(self):
        payload = json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False})
        proc = subprocess.run([sys.executable, SOLVE], input=payload,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 10700})

    def test_cli_missing_key_exits_2_without_traceback(self):
        payload = json.dumps({"items": [{"price": 10000, "qty": 1}]})
        proc = subprocess.run([sys.executable, SOLVE], input=payload,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_cli_bad_json_exits_2(self):
        proc = subprocess.run([sys.executable, SOLVE], input="{",
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
