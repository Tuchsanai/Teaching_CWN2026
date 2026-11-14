import json
import subprocess
import sys
import unittest

from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10_000_000, "platinum", False), 20000)
        self.assertEqual(cashback(500_000, "platinum", False), 20000)
        self.assertEqual(cashback(500_000, "gold", True), 20000)

    def test_rounding(self):
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10100, "gold", False), 253)     # 252.5 -> half up
        # ปัดหลังคูณสองเท่า: 150.495*2 = 300.99 -> 301
        self.assertEqual(cashback(10033, "silver", True), 301)

    def test_invalid(self):
        for a in (-1, 1.5, "100", None, True):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        with self.assertRaises(ValueError):
            cashback(10000, "bronze", False)
        with self.assertRaises(ValueError):
            cashback(10000, "gold", 1)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input=json.dumps(
            {"amount": 10000, "tier": "gold", "birthday": True}),
            capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout), {"cashback": 500})
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount": -5, "tier": "gold", "birthday": false}',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("error", json.loads(r.stdout))


if __name__ == "__main__":
    unittest.main()
