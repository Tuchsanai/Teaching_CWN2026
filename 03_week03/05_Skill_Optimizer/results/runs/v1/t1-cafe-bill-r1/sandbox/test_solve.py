import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_small_no_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_discount(self):
        # 50000 -> 47500 -> 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_just_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both_discounts(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_rounding_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        bad = [
            ([{"price": 1.0, "qty": 1}], False),
            ([{"price": 100, "qty": 0}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 100, "qty": 1}], 1),
            ("x", False),
            ([{"price": 100}], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        rc, out, _ = self._cli(json.dumps(
            {"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 10700})

    def test_cli_errors(self):
        for text in ["not json", "{}", "[]",
                     '{"items": [{"price": "1", "qty": 1}], "member": false}']:
            rc, out, err = self._cli(text)
            self.assertEqual(rc, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
