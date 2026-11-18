import json
import subprocess
import sys
import unittest

from solve import cashback


class T(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_rates(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10_000_000, "platinum", False), 20000)
        self.assertEqual(cashback(500_000, "platinum", True), 20000)
        self.assertEqual(cashback(500_000, "platinum", False), 20000)

    def test_rounding(self):
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertEqual(cashback(10100, "silver", False), 152)   # 151.5 -> half up

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), (True, "gold", False),
                     ("100", "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"amount": 10000, "tier": "gold", "birthday": True}))
        self.assertEqual(json.loads(r.stdout), {"cashback": 500})
        r = subprocess.run([sys.executable, "solve.py", '{"amount":-5,"tier":"gold","birthday":false}'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("error", json.loads(r.stdout))


if __name__ == "__main__":
    unittest.main()
