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
        self.assertEqual(cafe_bill([{"price": 100000, "qty": 1}], True), 91485)

    def test_single_rounding_half_up(self):
        self.assertEqual(cafe_bill([{"price": 1, "qty": 5}], False), 5)

    def test_invalid(self):
        for bad in ([{"price": 1.0, "qty": 1}], [{"price": 1, "qty": 0}],
                    [{"price": True, "qty": 1}], "x", [{"price": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([], 1)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run(json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 10700})
        p = run("{bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
