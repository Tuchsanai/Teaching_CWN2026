import json
import subprocess
import sys
import unittest

from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(0, 100), 0)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_rounding(self):
        # 200*0.0075*4 = 6.0 ; 10*0.0075*4=0.3 ; 70*0.0075*4=2.1 ; 2*.0075*... 
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(1234, 5), 46)   # 46.275
        self.assertEqual(late_fee(1100, 5), 41)   # 41.25
        self.assertEqual(late_fee(200, 5), 8)     # 7.5 -> 8 (floor would give 7)
        self.assertEqual(late_fee(10**12, 365), 15 * 10**10)

    def test_reject(self):
        for a, d in [(-1, 5), (5, -1), (5, 366), (1000.0, 5), (1000, 5.0),
                     ("1", 5), (1000, "5"), (True, 5), (1000, True), (None, 5),
                     (1000, None), (float("nan"), 5), (float("inf"), 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":100000,"days_late":10}',
                           capture_output=True, text=True)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 7500})
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":-1,"days_late":10}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


unittest.main() if __name__ == "__main__" else None
