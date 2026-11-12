import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_basic_vat_only(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_discount(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_and_threshold(self):
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], True), 45743)

    def test_qty_multiplies(self):
        self.assertEqual(cafe_bill([{"price": 6000, "qty": 10}], False), 60000 * 95 * 107 // 10000)

    def test_rounding_is_int(self):
        self.assertIsInstance(cafe_bill([{"price": 333, "qty": 1}], True), int)

    def test_invalid(self):
        bad = [
            ("x", False), ([{"price": 1.0, "qty": 1}], False),
            ([{"price": True, "qty": 1}], False), ([{"price": 1, "qty": 0}], False),
            ([{"price": 1}], False), ([{"price": 1, "qty": 1}], 1),
            ([{"price": -1, "qty": 1}], False), (None, False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        r = run(json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        for s in ("{bad", "{}", "[]"):
            r = run(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertEqual(r.stderr, "")


if __name__ == "__main__":
    unittest.main()
