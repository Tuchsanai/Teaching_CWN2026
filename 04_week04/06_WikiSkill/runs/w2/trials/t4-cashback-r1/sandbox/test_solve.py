import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_rounding(self):
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15

    def test_cap(self):
        self.assertEqual(cashback(400000, "gold", True), 20000)  # พอดี
        self.assertEqual(cashback(500000, "gold", True), 20000)  # เกิน
        self.assertEqual(cashback(600000, "platinum", False), 20000)  # 24000
        self.assertEqual(cashback(799999, "gold", False), 20000)

    def test_invalid(self):
        for args in [(-1, "gold", False), (10000.0, "gold", False),
                     (True, "gold", False), ("100", "gold", False),
                     (10000, "bronze", False), (10000, 1, False),
                     (10000, "gold", 1), (10000, "gold", "yes"),
                     (-5, "gold", True), (None, "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=payload,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli('{"amount": 10000, "tier": "gold", "birthday": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 500})

    def test_cli_error(self):
        r = self.run_cli('{"amount": -1, "tier": "gold", "birthday": false}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
