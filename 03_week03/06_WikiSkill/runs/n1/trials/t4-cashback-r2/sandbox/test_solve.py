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

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "silver", True), 15000)
        self.assertEqual(cashback(1000000, "gold", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)

    def test_half_up(self):
        # 10001*3/200 = 150.015 -> 150 ; 10033*3/200=150.495 -> 150 ; 10034 -> 150.51 -> 151
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10010*1/40 = 250.25; 10020/40=250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_errors(self):
        bad = [
            (-1, "gold", False), (10000.0, "gold", False), (True, "gold", False),
            ("100", "gold", False), (None, "gold", False),
            (10000, "bronze", False), (10000, 1, False), (10000, "gold", 1),
            (10000, "gold", None),
        ]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                cashback(*args)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        p = self.run_cli('{"amount": 20000, "tier": "gold", "birthday": true}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 1000})

    def test_cli_error(self):
        for t in ['{"amount": 20000.0, "tier": "gold", "birthday": true}',
                  '{"amount": 1}', 'not json', '[]']:
            p = self.run_cli(t)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
