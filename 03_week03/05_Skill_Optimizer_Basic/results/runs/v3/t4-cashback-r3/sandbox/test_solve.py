import json
import subprocess
import sys
import unittest

from solve import cashback


class TestCashback(unittest.TestCase):
    def test_silver(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_gold_platinum(self):
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)
        self.assertEqual(cashback(100000, "platinum", True), 8000)

    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "silver", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up(self):
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_invalid(self):
        for args in [(5.0, "gold", False), (True, "gold", False),
                     (-1, "gold", False), (100, "bronze", False),
                     (100, None, False), (100, "gold", 1)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        def run(text):
            p = subprocess.run([sys.executable, "solve.py"], input=text,
                               capture_output=True, text=True)
            return p.returncode, json.loads(p.stdout)
        self.assertEqual(run('{"amount": 10000, "tier": "silver", "birthday": false}'),
                         (0, {"ok": True, "result": 150}))
        code, out = run('{"amount": 1}')
        self.assertEqual((code, out["ok"]), (2, False))
        code, out = run('not json')
        self.assertEqual((code, out["ok"]), (2, False))


if __name__ == "__main__":
    unittest.main()
