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
        self.assertEqual(refund(20000, 0, False), 20000)

    def test_4(self):
        self.assertEqual(refund(20000, 0, True), 17500)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100(self):
        self.assertEqual(refund(10000, 100, True), 0)

    def test_paid_zero(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_80_restock(self):
        self.assertEqual(refund(10000, 80, True), 1750)


class NoDrift(unittest.TestCase):
    def test_1(self):
        # 999*0.7=699.3 -> 699
        self.assertEqual(refund(999, 30, False), 699)

    def test_2(self):
        # 1001*0.9*0.875=788.2875 -> 788
        self.assertEqual(refund(1001, 10, True), 788)

    def test_3(self):
        # 9*0.8*0.875... 9*80/100=7.2*0.875=6.3 -> 6
        self.assertEqual(refund(9, 20, True), 6)

    def test_4(self):
        # 1*0.5=0.5 -> 0 (floor)
        self.assertEqual(refund(1, 50, False), 0)


class Reject(unittest.TestCase):
    def test_all(self):
        bad = [(-1, 10, False), (100.0, 10, False), ("100", 10, False), (True, 10, False),
               (100, -1, False), (100, 101, False), (100, 10.0, False), (100, "10", False),
               (100, True, False), (100, 10, 1), (100, 10, "yes"), (100, 10, None)]
        for a in bad:
            with self.subTest(a=a):
                with self.assertRaises(ValueError):
                    refund(*a)

    def test_reject_before_zero_branch(self):
        with self.assertRaises(ValueError):
            refund(-5, 90, False)


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
