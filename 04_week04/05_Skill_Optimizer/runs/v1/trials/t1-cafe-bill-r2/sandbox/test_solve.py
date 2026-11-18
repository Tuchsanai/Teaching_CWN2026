import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_discount(self):
        # 50000 * .95 * 1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_just_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        # 100000 * .95 * .9 * 1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_rounding_half_up(self):
        # 5 * 1.07 = 5.35 -> 5 ; 10*1.07=10.7 -> 11
        self.assertEqual(cafe_bill([{"price": 5, "qty": 1}], False), 5)
        self.assertEqual(cafe_bill([{"price": 10, "qty": 1}], False), 11)

    def test_invalid(self):
        for items, m in [([{"price": 1.5, "qty": 1}], False),
                         ([{"price": 1, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 1, "qty": 1}], 1),
                         (None, False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"items": [{"price": 10000, "qty": 2}], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 21400})

    def test_cli_error(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="xx")
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
