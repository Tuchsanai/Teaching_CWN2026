import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class T(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50000 * 95 * 107 // 10000)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both(self):
        self.assertEqual(cafe_bill([{"price": 100000, "qty": 1}], True), 91485)

    def test_rounding_half_up(self):
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)  # 53.5

    def test_invalid(self):
        for bad in ([], [{"price": 1.5, "qty": 1}], [{"price": 1, "qty": 0}],
                    [{"price": True, "qty": 1}], "x"):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1, "qty": 1}], 1)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input=json.dumps(
            {"items": [{"price": 10000, "qty": 1}], "member": False}),
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = subprocess.run([sys.executable, "solve.py"], input="zz",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
