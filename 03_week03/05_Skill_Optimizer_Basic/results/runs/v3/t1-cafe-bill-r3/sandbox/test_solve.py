import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_small_no_member(self):
        # 10000 * 107 = 10700 exactly
        self.assertEqual(cafe_bill([{"price": 5000, "qty": 2}], False), 10700)

    def test_threshold_discount(self):
        # 50000 * 0.95 * 1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        # 49900 no discount: 49900*1.07 = 53393
        self.assertEqual(cafe_bill([{"price": 49900, "qty": 1}], False), 53393)

    def test_member_only(self):
        # 10000 * 0.9 * 1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both_discounts(self):
        # 100000 * 0.95 * 0.9 * 1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 4}], True), 91485)

    def test_invalid(self):
        for items, m in [("x", False), ([{"price": 1.0, "qty": 1}], False),
                         ([{"price": 100, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 100, "qty": 1}], 1)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli_ok_and_error(self):
        r = subprocess.run([sys.executable, "solve.py"], input=json.dumps(
            {"items": [{"price": 5000, "qty": 2}], "member": False}),
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = subprocess.run([sys.executable, "solve.py"], input="{bad",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
