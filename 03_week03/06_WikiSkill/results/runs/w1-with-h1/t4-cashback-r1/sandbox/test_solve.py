import json
import subprocess
import sys
import unittest

from solve import cashback


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
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
        # 10033*0.015 = 150.495 -> 150 ; 10034 -> 150.51 -> 151
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10010*0.025 = 250.25; 10020*0.025=250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_birthday_single_round(self):
        # 10020 gold: 250.5*2 = 501 exact (rounding first would give 502)
        self.assertEqual(cashback(10020, "gold", True), 501)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(10**9, "silver", False), 20000)

    def test_invalid(self):
        bad = [
            (100.0, "gold", False), (True, "gold", False), ("100", "gold", False),
            (None, "gold", False), (-1, "gold", False),
            (20000, "Gold", False), (20000, None, False), (20000, 1, False),
            (20000, "bronze", False),
            (20000, "gold", 1), (20000, "gold", None), (20000, "gold", "True"),
        ]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                cashback(*a)

    def test_cli(self):
        r = run(json.dumps({"amount": 20000, "tier": "gold", "birthday": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 1000})
        for p in ['{"amount": 1.5, "tier": "gold", "birthday": true}',
                  'not json', '{"amount": 1}', '[]']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
