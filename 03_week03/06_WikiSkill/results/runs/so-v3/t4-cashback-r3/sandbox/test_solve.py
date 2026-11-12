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
        self.assertEqual(cashback(10000, "silver", True), 300)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(300000, "platinum", False), 12000)
        self.assertEqual(cashback(300000, "platinum", True), 20000)
        self.assertEqual(cashback(10000000, "silver", False), 20000)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15 -> 150
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5 -> 152

    def test_invalid(self):
        for args in [(5.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (10000, "bronze", False), (10000, None, False), (10000, "gold", 1),
                     ("100", "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount": 10000, "tier": "gold", "birthday": false}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 250})
        for bad in ["{oops", '{"amount": 10000}', "[]", '{"amount": 1.5, "tier": "gold", "birthday": false}']:
            p = subprocess.run([sys.executable, "solve.py"], input=bad, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
