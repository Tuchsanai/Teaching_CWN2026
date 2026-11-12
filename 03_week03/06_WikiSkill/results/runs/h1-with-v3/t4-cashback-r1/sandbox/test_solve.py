import json
import os
import subprocess
import sys
import unittest

from solve import cashback

SOLVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solve.py")


def run_cli(text):
    proc = subprocess.run(
        [sys.executable, SOLVE], input=text, capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


class CashbackTests(unittest.TestCase):
    def test_rates_without_birthday(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_doubles(self):
        self.assertEqual(cashback(10000, "silver", True), 300)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_below_minimum_gets_zero(self):
        self.assertEqual(cashback(9999, "platinum", False), 0)
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_minimum_boundary_is_included(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_cap_200_baht_per_bill(self):
        self.assertEqual(cashback(10000000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "gold", True), 20000)

    def test_half_up_rounding_at_final_step(self):
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5 -> 152
        self.assertEqual(cashback(10300, "silver", False), 155)  # 154.5 -> 155

    def test_result_is_int(self):
        self.assertIs(type(cashback(10300, "silver", True)), int)

    def test_invalid_tier_raises(self):
        for tier in ("bronze", "Gold", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, tier, False)

    def test_invalid_amount_raises(self):
        for amount in (1e4, True, "10000", None, -1):
            with self.assertRaises(ValueError):
                cashback(amount, "gold", False)

    def test_invalid_birthday_raises(self):
        for birthday in (1, 0, "yes", None):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", birthday)


class CliTests(unittest.TestCase):
    def test_cli_success(self):
        code, out, _ = run_cli(json.dumps({"amount": 10000, "tier": "silver", "birthday": False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 150})

    def test_cli_missing_key(self):
        code, out, err = run_cli(json.dumps({"amount": 10000, "tier": "gold"}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)

    def test_cli_bad_json(self):
        code, out, err = run_cli("{not json")
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)

    def test_cli_invalid_tier(self):
        code, out, err = run_cli(json.dumps({"amount": 10000, "tier": "bronze", "birthday": True}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
