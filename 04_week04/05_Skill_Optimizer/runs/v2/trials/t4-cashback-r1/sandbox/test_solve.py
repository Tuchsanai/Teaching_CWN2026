import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_basic_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_only_gold_platinum(self):
        self.assertEqual(cashback(10000, "silver", True), 150)
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_floor_rounding(self):
        # 10001*15/1000 = 150.015 -> 150 ; 10039*15/1000=150.585 -> 150
        self.assertEqual(cashback(10039, "silver", False), 150)
        self.assertEqual(cashback(10039, "gold", False), 250)

    def test_cap(self):
        self.assertEqual(cashback(10_000_000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_invalid_inputs(self):
        bad = [(1.5, "gold", False), (True, "gold", False), (-1, "gold", False),
               ("100", "gold", False), (None, "gold", False),
               (10000, "bronze", False), (10000, None, False), (10000, ["a"], False),
               (10000, "gold", 1), (10000, "gold", None)]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                cashback(*args)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        p = self.run_cli('{"amount": 10000, "tier": "gold", "birthday": true}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 500})

    def test_cli_errors(self):
        for text in ["not json", "{}", "[1]",
                     '{"amount": 1.5, "tier": "gold", "birthday": false}']:
            p = self.run_cli(text)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
