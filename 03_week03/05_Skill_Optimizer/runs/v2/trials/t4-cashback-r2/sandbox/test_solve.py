import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_basic_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double_gold_platinum(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_birthday_silver_no_bonus(self):
        self.assertEqual(cashback(10000, "silver", True), 150)

    def test_floor_rounding(self):
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(10039, "gold", False), 250)
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10100, "silver", False), 151)
        self.assertEqual(cashback(10001, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_invalid(self):
        for args in [(1.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (100, "bronze", False), (100, None, False), (100, "gold", 1)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input='{"amount": 10000, "tier": "gold", "birthday": true}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 500})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="x")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
