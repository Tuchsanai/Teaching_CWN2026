import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_discount(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both(self):
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], True), 45743)

    def test_invalid(self):
        for bad in ([{"price": 1.0, "qty": 1}], [{"price": 1, "qty": 0}],
                    [{"price": True, "qty": 1}], [], "x", [{"price": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 1, "qty": 1}], 1)

    def test_cli(self):
        inp = json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False})
        r = subprocess.run([sys.executable, "solve.py"], input=inp,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})

    def test_cli_bad(self):
        r = subprocess.run([sys.executable, "solve.py"], input="{bad",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
