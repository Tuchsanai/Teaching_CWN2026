import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        # 50000 * 95 * 107 = 508250000 -> 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49900, "qty": 1}], False), 53393)

    def test_member(self):
        # 10000 * 0.9 * 1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both_discounts(self):
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

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input='{"items": [{"price": 10000, "qty": 1}], "member": true}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 9630})

    def test_cli_bad(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="{bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
