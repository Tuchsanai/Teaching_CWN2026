import json
import subprocess
import sys
import unittest

from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, True), 8750)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(0, 10, True), 0)

    def test_boundary(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_rounding(self):
        # 1*0.5*0.875 = 0.4375 -> 0 ; 4*0.5*0.875=1.75 -> 2
        self.assertEqual(refund(4, 50, True), 2)
        # 1 * 50% = 0.5 -> 1 (half-up)
        self.assertEqual(refund(1, 50, False), 1)
        # 12 * 0.5 *0.875 = 5.25 -> 5 ; 36*0.5*0.875=15.75 -> 16
        self.assertEqual(refund(36, 50, True), 16)

    def test_big(self):
        self.assertEqual(refund(10**12, 0, False), 10**12)

    def test_reject(self):
        for args in [(-1, 0, True), (1, -1, True), (1, 101, True), (1.0, 0, True),
                     ("3", 0, True), (True, 0, True), (None, 0, True),
                     (float("nan"), 0, True), (1, 5.0, True), (1, True, True),
                     (1, 0, 1), (1, 0, None)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"paid": 10000, "used_percent": 50, "restock": True}))
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4375})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"paid": -1, "used_percent": 50, "restock": True}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
