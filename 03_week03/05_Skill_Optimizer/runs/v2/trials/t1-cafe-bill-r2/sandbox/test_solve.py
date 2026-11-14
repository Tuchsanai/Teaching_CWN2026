import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        # 10000 * 107 / 100 = 10700
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000 * 95 * 107 / 10000 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member(self):
        # 10000 * 90 * 107 / 10000 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both_discounts(self):
        # 100000 * 95 * 90 * 107 / 1000000 = 91485
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_half_up_single_rounding(self):
        # 5 * 107 / 100 = 5.35 -> 5 ; 50 * 107 / 100 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 5, "qty": 1}], False), 5)
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        bad = [
            ([{"price": 1.0, "qty": 1}], False),
            ([{"price": 1, "qty": 0}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 1, "qty": 1}], 1),
            ("x", False),
            ([{"price": 1}], False),
            ([{"price": -1, "qty": 1}], False),
        ]
        for items, member in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, member)

    def _run(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout

    def test_cli_ok(self):
        code, out = self._run(json.dumps(
            {"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 10700})

    def test_cli_errors(self):
        for text in ["not json", "{}", "[]", '{"items": [], "member": "yes"}']:
            code, out = self._run(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])


if __name__ == "__main__":
    unittest.main()
