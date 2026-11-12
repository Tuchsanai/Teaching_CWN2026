import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_minimum_boundary(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_birthday_double(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(1000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up(self):
        # 10010 * 15 = 150150 -> 150.15 -> 150 ; 10050 * 15 = 150750 -> 150.75 -> 151
        self.assertEqual(cashback(10010, "silver", False), 150)
        self.assertEqual(cashback(10050, "silver", False), 151)
        # exactly .5: 10030 * 15 = 150450 -> no; 10100 * 25 = 252500 -> 252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)

    def test_invalid(self):
        for args in [(1.0, "gold", False), (True, "gold", False), ("1", "gold", False),
                     (None, "gold", False), (-1, "gold", False), (100, "bronze", False),
                     (100, None, False), (100, ["gold"], False), (20000, "gold", 1),
                     (20000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self.run_cli('{"amount": 20000, "tier": "gold", "birthday": true}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 1000})

    def test_cli_errors(self):
        for text in ["not json", "[]", '{"amount": 20000}',
                     '{"amount": 5.0, "tier": "gold", "birthday": false}']:
            code, out, err = self.run_cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
