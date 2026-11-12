import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)

    def test_rounding_half_up(self):
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15

    def test_invalid(self):
        for args in [(5.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (10000, "bronze", False), (10000, "gold", 1), (None, "gold", True)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run('{"amount": 10000, "tier": "gold", "birthday": false}')
        self.assertEqual((p.returncode, json.loads(p.stdout)), (0, {"ok": True, "result": 250}))
        for bad in ['{bad', '{"amount": 1}', '[]', '{"amount":1.5,"tier":"gold","birthday":true}']:
            p = run(bad)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertEqual(p.stderr, "")


if __name__ == "__main__":
    unittest.main()
