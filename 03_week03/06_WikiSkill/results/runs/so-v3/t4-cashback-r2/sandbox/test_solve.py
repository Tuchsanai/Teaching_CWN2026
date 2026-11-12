import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_rates_at_minimum(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(20000, "silver", True), 600)

    def test_half_up(self):
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5

    def test_cap(self):
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_invalid(self):
        for args in [(5.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (100, "bronze", False), (100, None, False), (100, "gold", 1)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        def run(s):
            p = subprocess.run([sys.executable, "solve.py"], input=s, capture_output=True, text=True)
            return p.returncode, json.loads(p.stdout)
        self.assertEqual(run('{"amount": 10000, "tier": "gold", "birthday": false}'), (0, {"ok": True, "result": 250}))
        self.assertEqual(run('{"amount": 1}')[0], 2)
        self.assertEqual(run('oops')[0], 2)


if __name__ == "__main__":
    unittest.main()
