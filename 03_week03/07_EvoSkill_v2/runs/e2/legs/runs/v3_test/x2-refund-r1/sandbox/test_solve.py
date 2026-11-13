import json
import subprocess
import sys
import unittest

from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(0, 10, True), 0)

    def test_boundary(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)
        self.assertEqual(refund(1000, 0, True), 875)

    def test_rounding(self):
        # 1*0.875 = 0.875 -> 1 ; 4*0.5*0.875=1.75 -> 2
        self.assertEqual(refund(1, 0, True), 1)
        # 1 * 50% = 0.5 -> half-up 1 (floor/banker's would give 0)
        self.assertEqual(refund(1, 50, False), 1)
        # 3*0.875 = 2.625 -> 3
        self.assertEqual(refund(3, 0, True), 3)
        # 4 * 0.875 * 0.99 = 3.465 -> 3
        self.assertEqual(refund(4, 1, True), 3)

    def test_big(self):
        self.assertEqual(refund(10**12, 0, True), 875 * 10**9)

    def test_reject(self):
        bad = [(-1, 0, False), (10, -1, False), (10, 101, False),
               (10.0, 0, False), ("3", 0, False), (True, 0, False),
               (None, 0, False), (float("nan"), 0, False),
               (10, 5.0, False), (10, True, False), (10, 5, 1),
               (10, 5, None), (10, 5, "True")]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                refund(*a)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True,
                           input='{"paid":10000,"used_percent":50,"restock":true}')
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4375})
        self.assertEqual(p.returncode, 0)
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True,
                           input='{"paid":-1,"used_percent":50,"restock":true}')
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
