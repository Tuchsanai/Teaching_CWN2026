import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "gold", True), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_rates(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_double(self):
        self.assertEqual(cashback(100000, "silver", True), 3000)

    def test_half_up_once(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)

    def test_invalid(self):
        for args in [(5.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (10000, "bronze", False), (10000, "gold", 1), (None, "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":100000,"tier":"gold","birthday":false}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 2500})
        p = subprocess.run([sys.executable, "solve.py"], input='{bad', capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
