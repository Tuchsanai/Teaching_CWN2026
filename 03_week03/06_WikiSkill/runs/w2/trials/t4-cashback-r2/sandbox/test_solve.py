import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "silver", True), 600)

    def test_rounding(self):
        # 10001*0.015 = 150.015 -> 150 ; 10033*0.015 = 150.495 -> 150
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(10033, "silver", False), 150)
        # 10034*0.015 = 150.51 -> 151
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10020*0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_cap(self):
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**8, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_invalid(self):
        for args in [(-1, "gold", False), (20000.0, "gold", False),
                     (True, "gold", False), ("100", "gold", False),
                     (20000, "bronze", False), (20000, 1, False),
                     (20000, "gold", 1), (20000, "gold", "yes"),
                     (-1, "gold", True)]:
            with self.assertRaises(ValueError, msg=str(args)):
                cashback(*args)

    def run_cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=payload,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        p = self.run_cli('{"amount": 20000, "tier": "silver", "birthday": true}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 600})

    def test_cli_error(self):
        p = self.run_cli('{"amount": -5, "tier": "silver", "birthday": true}')
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
