import json
import subprocess
import sys
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_2(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_3(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_4(self):
        self.assertEqual(refund(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_80_restock(self):
        self.assertEqual(refund(10000, 80, True), 1750)


class NoDrift(unittest.TestCase):
    def test_1(self):  # 999*0.99*0.875=865.4 -> floor 865
        self.assertEqual(refund(999, 1, True), 865)

    def test_2(self):  # 1001*0.67=670.67 -> 670 (ไม่ half-up)
        self.assertEqual(refund(1001, 33, False), 670)

    def test_3(self):  # 1*0.875 -> 0
        self.assertEqual(refund(1, 0, True), 0)


class Reject(unittest.TestCase):
    def test_neg_paid(self):
        with self.assertRaises(ValueError):
            refund(-1, 10, False)

    def test_float(self):
        with self.assertRaises(ValueError):
            refund(100.0, 10, False)

    def test_pct_range(self):
        for p in (-1, 101):
            with self.assertRaises(ValueError):
                refund(100, p, False)

    def test_str(self):
        with self.assertRaises(ValueError):
            refund(100, "10", False)

    def test_bool_int(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)

    def test_flag(self):
        with self.assertRaises(ValueError):
            refund(100, 10, 1)

    def test_reject_before_zero(self):
        with self.assertRaises(ValueError):
            refund(100, 101, False)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"paid": 10000, "used_percent": 50, "restock": True}),
                         (0, {"ok": True, "result": 4375}))

    def test_err(self):
        code, out = self.run_cli({"paid": -5, "used_percent": 50, "restock": True})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
