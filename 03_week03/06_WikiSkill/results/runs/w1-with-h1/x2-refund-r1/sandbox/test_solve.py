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
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_half_up(self):
        # 1*99/100 = 0.99 -> 1 ; 50*99/100*7/8 ... use exact cases
        self.assertEqual(refund(1, 50, False), 1)      # 0.5 -> 1
        # 10 * 80/100 * 7/8 = 7 exactly; 2*... 6*50/100*7/8=2.625 -> 3
        self.assertEqual(refund(6, 50, True), 3)
        # 4*50/100*7/8 = 1.75 -> 2 ; 1*100/100*7/8=0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)
        # 4 * 7/8 = 3.5 -> 4 (single rounding)
        self.assertEqual(refund(4, 0, True), 4)

    def test_invalid(self):
        for args in [(1.0, 1, True), (True, 1, True), ("1", 1, True), (None, 1, True),
                     (-1, 1, True), (1, 1.0, True), (1, True, True), (1, "1", True),
                     (1, None, True), (1, -1, True), (1, 101, True),
                     (1, 1, 1), (1, 1, None), (1, 1, "True"), (1, 1, 0)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        r = run(json.dumps({"paid": 10000, "used_percent": 50, "restock": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        r = run(json.dumps({"paid": 1.5, "used_percent": 50, "restock": True}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(run("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
