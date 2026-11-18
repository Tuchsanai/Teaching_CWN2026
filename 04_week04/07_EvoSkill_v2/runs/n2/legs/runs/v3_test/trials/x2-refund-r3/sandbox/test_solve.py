import json
import subprocess
import sys
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_2(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_3(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_4(self):
        self.assertEqual(refund(10000, 0, True), 8750)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_80_restock(self):
        self.assertEqual(refund(10000, 80, True), 1750)


class NoDrift(unittest.TestCase):
    def test_floor(self):
        # 999*0.7*0.875 = 611.8875 -> 611
        self.assertEqual(refund(999, 30, True), 611)

    def test_floor_2(self):
        # 1001*0.99 = 990.99 -> 990
        self.assertEqual(refund(1001, 1, False), 990)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 10, False), (100, -1, False), (100, 101, False),
                     (100.0, 10, False), (100, 10.0, False), ("100", 10, False),
                     (True, 10, False), (100, True, False), (100, 10, 1), (100, 10, None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"paid": 10000, "used_percent": 50, "restock": True}),
                         (0, {"ok": True, "result": 4375}))

    def test_err(self):
        code, out = self.run_cli({"paid": -1, "used_percent": 50, "restock": True})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
