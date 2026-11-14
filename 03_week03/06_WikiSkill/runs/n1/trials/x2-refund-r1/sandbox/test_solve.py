import json
import subprocess
import sys
import unittest

from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 10, True), 0)

    def test_half_up(self):
        # 10*50/100*7/8 = 4.375 -> 4 ; 12*50% *7/8 = 5.25 -> 5
        self.assertEqual(refund(10, 50, True), 4)
        # 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 4*50%*7/8 = 1.75 -> 2
        self.assertEqual(refund(4, 50, True), 2)

    def test_errors(self):
        for a in [(-1, 10, True), (100, -1, True), (100, 101, True),
                  (100.0, 10, True), (100, 10.0, True), (True, 10, True),
                  (100, True, True), (100, 10, 1), ("100", 10, True),
                  (100, 10, None)]:
            with self.assertRaises(ValueError):
                refund(*a)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"paid": 10000, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        for s in ['{"paid": 100.0, "used_percent": 5, "restock": true}',
                  '{"paid": 100}', 'bad', '[1]']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
