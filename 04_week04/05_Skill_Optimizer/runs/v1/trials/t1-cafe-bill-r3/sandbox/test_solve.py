import json
import subprocess
import sys
import unittest

from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member_stack(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_rounding(self):
        self.assertEqual(cafe_bill([{"price": 1, "qty": 5}], False), 5)
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [([{"price": 1.5, "qty": 1}], False),
                         ([{"price": 1, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 1, "qty": 1}], 1),
                         ("x", False), ([{"price": 1}], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"items": [{"price": 10000, "qty": 2}], "member": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 21400})

    def test_cli_error(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
