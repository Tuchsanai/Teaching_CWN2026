import json
import os
import subprocess
import sys
import unittest

from solve import cafe_bill

HERE = os.path.dirname(os.path.abspath(__file__))


class CafeBillTests(unittest.TestCase):
    def test_below_threshold_vat_only(self):
        # 499 บาท -> ไม่ลด 5% แค่บวก VAT: 49900 * 1.07 = 53393
        self.assertEqual(cafe_bill([{"price": 49900, "qty": 1}], False), 53393)

    def test_threshold_bulk_discount(self):
        # 500 บาท -> ลด 5%: 47500 * 1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member_below_threshold(self):
        # 100 บาท -> สมาชิกลด 10%: 9000 * 1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_with_threshold_half_up_rounding(self):
        # 50000 -> *0.95 = 47500 -> *0.9 = 42750 -> *1.07 = 45742.5 -> ปัดขึ้น 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_multiple_items_sum_before_discount(self):
        # 2550*2 + 4900*3 = 19800 -> *1.07 = 21186
        items = [{"price": 2550, "qty": 2}, {"price": 4900, "qty": 3}]
        self.assertEqual(cafe_bill(items, False), 21186)

    def test_empty_items_and_free_item(self):
        self.assertEqual(cafe_bill([], False), 0)
        self.assertEqual(cafe_bill([{"price": 0, "qty": 5}], True), 0)

    def test_rejects_bad_types_and_ranges(self):
        bad_cases = [
            ([{"price": 5.0, "qty": 1}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ("not a list", False),
            ([{"price": 100, "qty": 1}], "yes"),
            ([{"price": 100, "qty": 1}], None),
        ]
        for items, member in bad_cases:
            with self.subTest(items=items, member=member):
                with self.assertRaises(ValueError):
                    cafe_bill(items, member)

    def test_cli_success(self):
        payload = json.dumps({"items": [{"price": 50000, "qty": 1}], "member": False})
        proc = subprocess.run([sys.executable, os.path.join(HERE, "solve.py")],
                              input=payload, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 50825})

    def test_cli_errors_exit_2_without_traceback(self):
        for payload in ["{not json", json.dumps({"items": []}), "[1, 2]",
                        json.dumps({"items": [{"price": 1.5, "qty": 1}], "member": False})]:
            with self.subTest(payload=payload):
                proc = subprocess.run([sys.executable, os.path.join(HERE, "solve.py")],
                                      input=payload, capture_output=True, text=True)
                self.assertEqual(proc.returncode, 2)
                self.assertFalse(json.loads(proc.stdout)["ok"])
                self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
