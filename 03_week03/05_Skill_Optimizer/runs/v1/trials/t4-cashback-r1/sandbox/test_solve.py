import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "silver", False), 0)

    def test_rates_at_minimum(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_rounding_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertIsInstance(cashback(12345, "gold", False), int)

    def test_invalid(self):
        for args in [(1.5, "gold", False), (True, "gold", False),
                     (-1, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, "gold", 1),
                     ("10000", "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        p = self.run_cli('{"amount": 10000, "tier": "gold", "birthday": false}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 250})

    def test_cli_errors(self):
        for text in ["not json", "{}", "[]",
                     '{"amount": 1.5, "tier": "gold", "birthday": false}']:
            p = self.run_cli(text)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
