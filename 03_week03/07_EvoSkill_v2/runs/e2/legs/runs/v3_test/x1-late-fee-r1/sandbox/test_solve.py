import json
import subprocess
import sys
import unittest

from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(200000, 5), 7500)
        self.assertEqual(late_fee(100000, 100), 15000)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(0, 50), 0)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_rounding(self):
        # 10*4*0.0075=0.3 ->0 ; 50*4*.0075=1.5 ->2 (half-up)
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(10**12, 365), 15 * 10**10)

    def test_reject(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5),
                     (100, None), (float("nan"), 5), (100, float("inf"))]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount":100000,"days_late":10}',
                           capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 7500})
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount":-1,"days_late":10}',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


unittest.main() if __name__ == "__main__" else None
