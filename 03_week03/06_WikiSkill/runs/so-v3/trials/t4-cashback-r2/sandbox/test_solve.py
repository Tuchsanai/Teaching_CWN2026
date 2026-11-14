import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_min_boundary(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_rates(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_gold_platinum_only(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "platinum", True), 8000)
        self.assertEqual(cashback(100000, "silver", True), 1500)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)

    def test_floor(self):
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10040, "silver", False), 150)  # 150.6 -> floor

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.0, "gold", False), (True, "gold", False),
                     (10000, "bronze", False), (10000, "gold", 1), (None, "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":100000,"tier":"gold","birthday":true}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), '{"ok": true, "result": 5000}')
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":1}', capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('"ok": false', p.stdout)


if __name__ == "__main__":
    unittest.main()
