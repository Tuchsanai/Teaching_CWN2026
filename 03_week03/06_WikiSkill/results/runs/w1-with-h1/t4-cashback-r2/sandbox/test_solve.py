import json
import subprocess
import sys
import unittest

from solve import cashback


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class CashbackTest(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10000, "platinum", True), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)  # 150.015

    def test_half_up(self):
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5

    def test_single_rounding_with_birthday(self):
        # 10033*0.015*2 = 301.0 - 1.. exact: 10033*0.03 = 300.99 -> 301
        self.assertEqual(cashback(10033, "silver", True), 301)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(300000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)

    def test_invalid(self):
        bad = [
            (10000.0, "gold", False), (True, "gold", False), ("100", "gold", False),
            (None, "gold", False), (-1, "gold", False),
            (10000, "Gold", False), (10000, "bronze", False), (10000, None, False),
            (10000, 1, False),
            (10000, "gold", 1), (10000, "gold", None), (10000, "gold", "True"),
        ]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                cashback(*args)

    def test_cli(self):
        r = run(json.dumps({"amount": 10100, "tier": "silver", "birthday": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 152})
        for p in ['{"amount": 1.5, "tier": "gold", "birthday": false}', "nope",
                  '{"amount": 10000}', "[]"]:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
