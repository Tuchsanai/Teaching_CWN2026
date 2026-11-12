import json
import subprocess
import sys
import unittest

from solve import refund


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)

    def test_threshold(self):
        # 80% -> 20% of 1000 = 200 ; 81% -> 0
        self.assertEqual(refund(1000, 79, False), 210)
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_half_up(self):
        # 1 * 50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 1*0.5*0.875 = 0.4375 -> 0
        self.assertEqual(refund(1, 50, True), 0)
        # 4 * 0.5... paid=12,used=50: 6*0.875=5.25 ->5 ; paid=4,used=0: 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)
        # single rounding: paid=10 used=75 -> 2.5 -> 3 (no restock)
        self.assertEqual(refund(10, 75, False), 3)
        # 10*0.25*0.875=2.1875 -> 2
        self.assertEqual(refund(10, 75, True), 2)

    def test_invalid(self):
        bad = [(1.0, 1, True), (True, 1, True), ("1", 1, True), (None, 1, True), (-1, 1, True),
               (1, 1.0, True), (1, True, True), (1, "1", True), (1, None, True),
               (1, -1, True), (1, 101, True),
               (1, 1, 1), (1, 1, None), (1, 1, "True"), (1, 1, 0)]
        for a in bad:
            with self.assertRaises(ValueError):
                refund(*a)

    def test_cli(self):
        r = run(json.dumps({"paid": 10000, "used_percent": 50, "restock": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        for p in ['{"paid": 1.5, "used_percent": 1, "restock": true}', 'xx', '{"paid": 1}']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
