import json
import subprocess
import sys
import unittest

from solve import cashback


class CashbackTests(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_minimum_boundary(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_rounding_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10100, "gold", False), 253)    # 252.5 -> 253
    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)  # 400 baht -> cap
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_returns_int(self):
        self.assertIsInstance(cashback(12345, "gold", True), int)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), ("100", "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises((ValueError, TypeError), msg=args):
                cashback(*args)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input='{"amount": 50000, "tier": "gold", "birthday": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"cashback": 2500})
        r = subprocess.run([sys.executable, "solve.py", '{"amount": -5, "tier": "gold", "birthday": true}'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("error", json.loads(r.stdout))
        r = subprocess.run([sys.executable, "solve.py", "not json"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
