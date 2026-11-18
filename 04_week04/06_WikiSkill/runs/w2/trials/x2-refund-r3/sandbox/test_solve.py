import json
import subprocess
import sys
import unittest

from solve import refund


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, True), 8750)
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 10, True), 0)

    def test_rounding(self):
        # 101*0.5*0.875 = 44.1875 -> 44 ; 100*0.99... 
        self.assertEqual(refund(101, 50, True), 44)
        self.assertEqual(refund(1, 50, False), 1)   # 0.5 -> 1 (half up)
        self.assertEqual(refund(3, 50, True), 1)    # 1.3125 -> 1

    def test_invalid(self):
        for args in [(-1, 0, False), (10, -1, False), (10, 101, False),
                     (10.0, 0, False), (10, 5.0, False), (True, 0, False),
                     (10, True, False), (10, 0, 1), ("10", 0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"paid":10000,"used_percent":50,"restock":true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        r = self.run_cli('{"paid":-1,"used_percent":50,"restock":true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
