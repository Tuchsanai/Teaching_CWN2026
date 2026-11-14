import json
import subprocess
import sys
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(20000, "silver", False), 300)

    def test_gold(self):
        self.assertEqual(cashback(40000, "gold", False), 1000)

    def test_platinum_birthday(self):
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_gold_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)


class Boundary(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "gold", False), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_zero(self):
        self.assertEqual(cashback(0, "platinum", True), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_birthday(self):
        self.assertEqual(cashback(300000, "platinum", True), 20000)

    def test_silver_birthday_no_double(self):
        self.assertEqual(cashback(20000, "silver", True), 300)


class NoDrift(unittest.TestCase):
    def test_floor_1(self):
        self.assertEqual(cashback(10015, "platinum", True), 801)

    def test_floor_2(self):
        self.assertEqual(cashback(10020, "gold", True), 501)

    def test_floor_3(self):
        self.assertEqual(cashback(10001, "silver", False), 150)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            cashback(*a)

    def test_negative(self):
        self.bad(-1, "gold", False)

    def test_float(self):
        self.bad(20000.0, "gold", False)

    def test_str_amount(self):
        self.bad("20000", "gold", False)

    def test_bool_amount(self):
        self.bad(True, "gold", False)

    def test_tier(self):
        self.bad(20000, "bronze", False)

    def test_tier_type(self):
        self.bad(20000, None, False)

    def test_birthday(self):
        self.bad(20000, "gold", 1)

    def test_reject_before_min(self):
        self.bad(50, "bronze", False)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"amount": 20000, "tier": "platinum", "birthday": True}),
                         (0, {"ok": True, "result": 1600}))

    def test_error(self):
        code, out = self.run_cli({"amount": -5, "tier": "gold", "birthday": False})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
