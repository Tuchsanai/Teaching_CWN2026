import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_discount(self):
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], False), 50825)

    def test_just_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49900, "qty": 1}], False), 53393)

    def test_member_only(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_and_threshold_half_up(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_invalid_inputs(self):
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

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 10700})

    def test_cli_error(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="{bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
