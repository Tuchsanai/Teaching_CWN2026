import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "silver", False), 0)

    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up_rounding(self):
        # 10033 * 15 = 150495 -> 150.495 -> 150
        self.assertEqual(cashback(10033, "silver", False), 150)
        # 10010 * 15 = 150150 -> 150.15 -> 150 ; 10050*15=150750 -> 151
        self.assertEqual(cashback(10050, "silver", False), 151)
        # exact half: 10100*25=252500 -> 252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)

    def test_invalid(self):
        for args in [(1.0, "gold", False), (True, "gold", False),
                     (-1, "gold", False), ("5", "gold", False),
                     (None, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, "gold", 1),
                     (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self.run_cli('{"amount": 10000, "tier": "gold", "birthday": false}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 250})

    def test_cli_errors(self):
        for text in ["not json", "{}", "[1]",
                     '{"amount": 5.0, "tier": "gold", "birthday": false}']:
            code, out, err = self.run_cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
