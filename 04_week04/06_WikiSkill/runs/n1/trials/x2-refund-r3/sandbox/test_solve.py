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
        # 10 * 0.875 = 8.75 -> 9 ; 1*50/100=0.5 -> 1
        self.assertEqual(refund(10, 0, True), 9)
        self.assertEqual(refund(1, 50, False), 1)
        # 4 * 0.875 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_errors(self):
        for args in [(-1, 0, False), (100, -1, False), (100, 101, False),
                     (100.0, 0, False), (100, 10.0, False), (True, 0, False),
                     (100, True, False), (100, 10, 1), ("100", 0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"paid": 10000, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        r = self.run_cli('{"paid": 10000.0, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        r = self.run_cli('nope')
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
