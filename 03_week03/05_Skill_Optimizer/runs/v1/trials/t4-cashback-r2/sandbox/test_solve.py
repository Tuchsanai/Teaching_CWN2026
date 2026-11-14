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

    def test_birthday_double(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_rounding_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertEqual(cashback(10100, "silver", False), 152)   # 151.5

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), (True, "gold", False),
                     ("1", "gold", False), (None, "gold", False),
                     (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run('{"amount": 100000, "tier": "gold", "birthday": true}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 5000})
        for bad in ['nope', '{"amount": 1}', '{"amount": 1.0, "tier": "gold", "birthday": false}']:
            p = run(bad)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
