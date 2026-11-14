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

    def test_birthday_only_gold_platinum(self):
        self.assertEqual(cashback(10000, "silver", True), 150)
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_floor_rounding(self):
        self.assertEqual(cashback(10040, "silver", False), 150)
        self.assertEqual(cashback(10099, "gold", False), 252)

    def test_invalid(self):
        for args in [(1.5, "gold", False), (True, "gold", False), (-1, "gold", False),
                     (100, "bronze", False), (100, ["x"], False), (100, "gold", 1),
                     (100, "gold", None), ("100", "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":10000,"tier":"gold","birthday":true}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), '{"ok": true, "result": 500}')
        p = subprocess.run([sys.executable, "solve.py"], input='nope', capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('"ok": false', p.stdout)
        self.assertEqual(p.stderr, "")


if __name__ == "__main__":
    unittest.main()
