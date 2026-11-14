import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_rounding(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 151.01

    def test_invalid(self):
        for args in [(1.5, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (10000, "bronze", False), (10000, "gold", 1), (None, "gold", False),
                     ("100", "gold", False), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout), p.stderr

    def test_cli_ok(self):
        code, out, _ = self.run_cli('{"amount": 10000, "tier": "gold", "birthday": false}')
        self.assertEqual((code, out), (0, {"ok": True, "result": 250}))

    def test_cli_errors(self):
        for t in ["not json", '{"amount": 1}', '{"amount": 1.5, "tier": "gold", "birthday": false}', "[]"]:
            code, out, err = self.run_cli(t)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
