import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_small_no_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member_stacks(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_half_up_single_rounding(self):
        self.assertEqual(cafe_bill([{"price": 150, "qty": 1}], False), 161)

    def test_invalid(self):
        for items, m in [([{"price": 1.0, "qty": 1}], False),
                         ([{"price": 1, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 1, "qty": 1}], 1),
                         ("x", False), ([], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        self.assertEqual(self._cli('{"items":[{"price":10000,"qty":1}],"member":false}'),
                         (0, {"ok": True, "result": 10700}))

    def test_cli_errors(self):
        for t in ['{bad', '{"items":[]}', '[]']:
            code, out = self._cli(t)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
