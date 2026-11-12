import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10030*0.015=150.45 ; 10100*0.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10033*0.015 = 150.495 -> 150 ; 10034*0.015=150.51 -> 151
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10010*0.025 = 250.25 ; birthday 500.5 -> 501 (single rounding)
        self.assertEqual(cashback(10010, "gold", True), 501)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(1000000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)

    def test_invalid(self):
        bad = [
            (100.0, "gold", False), (True, "gold", False), ("100", "gold", False),
            (None, "gold", False), (-1, "gold", False),
            (10000, "Gold", False), (10000, None, False), (10000, 1, False),
            (10000, "bronze", False),
            (10000, "gold", 1), (10000, "gold", None), (10000, "gold", "True"),
        ]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                cashback(*args)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli(json.dumps({"amount": 20000, "tier": "gold", "birthday": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 1000})

    def test_cli_error(self):
        for text in ['{"amount": 1.5, "tier": "gold", "birthday": false}', 'nope',
                     '{"amount": 1}', '[]']:
            r = self.run_cli(text)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
