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
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_rounding(self):
        # 1*0.5 = 0.5 -> 1 (half-up)
        self.assertEqual(refund(1, 50, False), 1)
        # 100*0.8*0.875 = 70
        self.assertEqual(refund(100, 20, True), 70)
        # 1*0.99*0.875=0.86625 -> 1
        self.assertEqual(refund(1, 1, True), 1)
        # 3*0.5*0.875=1.3125 -> 1 ; 4*0.5*0.875 = 1.75 -> 2
        self.assertEqual(refund(4, 50, True), 2)
        # exact .5: 4*0.875*... 1*... paid=4,used=0,restock => 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_big(self):
        self.assertEqual(refund(10**12, 0, False), 10**12)
        self.assertIsInstance(refund(10**12, 10, True), int)

    def test_reject(self):
        for args in [(-1, 0, False), (1, -1, False), (1, 101, False),
                     (1.0, 0, False), ("3", 0, False), (True, 0, False),
                     (None, 0, False), (1, 1.0, False), (1, True, False),
                     (1, 0, 1), (1, 0, None), (float("nan"), 0, False),
                     (float("inf"), 0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        def run(s):
            return subprocess.run([sys.executable, "solve.py"], input=s,
                                  capture_output=True, text=True)
        p = run('{"paid": 10000, "used_percent": 50, "restock": true}')
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4375})
        self.assertEqual(p.returncode, 0)
        p = run('{"paid": -1, "used_percent": 50, "restock": true}')
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
