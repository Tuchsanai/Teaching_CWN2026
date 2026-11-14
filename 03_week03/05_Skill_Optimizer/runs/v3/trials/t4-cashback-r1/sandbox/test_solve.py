import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_minimum_boundary(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_rates(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_only_gold_platinum(self):
        self.assertEqual(cashback(100000, "silver", True), 1500)
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "platinum", True), 8000)

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_floor_rounding(self):
        # 10001*15/1000 = 150.015 -> 150 ; 10033*15/1000=150.495 -> 150
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 150)  # 150.51 ปัดลง

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), (True, "gold", False),
                     (100, "bronze", False), (100, "gold", 1), (100, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"amount": 100000, "tier": "gold", "birthday": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 5000})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="x")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
