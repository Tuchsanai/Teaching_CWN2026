import json
import subprocess
import sys
import unittest

from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(200000, 5), 7500)
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 10), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_rounding(self):
        # 10*0.0075*4 = 0.3 -> 0 ; 50*0.03=1.5 -> 2 (half-up)
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(10, 20), 2)  # 1.5 -> 2

    def test_big(self):
        self.assertEqual(late_fee(10**12, 30), 15 * 10**10)

    def test_reject(self):
        bad = [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
               ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5),
               (100, None), (float("nan"), 5), (float("inf"), 5)]
        for a, d in bad:
            with self.assertRaises(ValueError, msg=(a, d)):
                late_fee(a, d)
        with self.assertRaises(ValueError):
            late_fee(100, 2.5)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"amount": 100000, "days_late": 10}))
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 7500})
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"amount": -1, "days_late": 10}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
