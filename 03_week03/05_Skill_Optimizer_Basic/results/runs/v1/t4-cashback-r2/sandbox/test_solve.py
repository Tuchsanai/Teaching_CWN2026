import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10_000_000, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)

    def test_rounding_half_up(self):
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495 -> 150
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5 -> 152

    def test_invalid(self):
        for args in [(5.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     ("1", "gold", False), (None, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, ["gold"], False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def _run(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self._run('{"amount": 10000, "tier": "gold", "birthday": false}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 250})

    def test_cli_errors(self):
        for text in ["not json", "[]", '{"amount": 10000}',
                     '{"amount": 1.0, "tier": "gold", "birthday": false}']:
            code, out, err = self._run(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
