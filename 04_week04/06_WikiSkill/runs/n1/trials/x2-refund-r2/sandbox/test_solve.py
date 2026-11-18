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

    def test_edges(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)

    def test_half_up(self):
        self.assertEqual(refund(1, 50, False), 1)   # 0.5 -> 1
        self.assertEqual(refund(10, 55, True), 4)   # 3.9375 -> 4
        self.assertEqual(refund(100, 79, True), 18) # 18.375 -> 18
        self.assertEqual(refund(4, 50, True), 2)    # 1.75 -> 2

    def test_errors(self):
        bad = [(-1, 0, False), (10, -1, False), (10, 101, False),
               (10.0, 0, False), (True, 0, False), (10, 5.0, False),
               (10, True, False), ("10", 0, False), (10, 0, 1), (10, 0, None)]
        for a in bad:
            with self.assertRaises(ValueError):
                refund(*a)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"paid": 10000, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        for s in ['{"paid": 100.0, "used_percent": 5, "restock": false}',
                  '{"paid": 1}', 'xx', '[]']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
