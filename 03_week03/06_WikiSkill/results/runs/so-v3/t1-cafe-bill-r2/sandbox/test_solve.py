import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        # 10000 * 107 / 100 = 10700
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_discount(self):
        # 50000 * 0.95 * 1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member_only(self):
        # 10000 * 0.9 * 1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_and_threshold(self):
        # 100000 * 0.95 * 0.9 * 1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_invalid(self):
        for items, m in [([{"price": 1.0, "qty": 1}], False),
                         ([{"price": 1, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 1, "qty": 1}], 1),
                         ("x", False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        code, out = self._cli(json.dumps(
            {"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual((code, out), (0, {"ok": True, "result": 10700}))

    def test_cli_errors(self):
        for text in ["not json", "{}", '{"items": [], "member": "x"}']:
            code, out = self._cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
