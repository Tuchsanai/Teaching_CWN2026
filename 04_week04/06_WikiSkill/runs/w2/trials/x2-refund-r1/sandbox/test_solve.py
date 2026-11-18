import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)

    def test_threshold(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 80, True), 1750)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_rounding(self):
        self.assertEqual(refund(1001, 50, False), 501)   # 500.5
        self.assertEqual(refund(1001, 50, True), 438)    # 437.9375
        self.assertEqual(refund(1, 50, False), 1)        # 0.5

    def test_invalid(self):
        for args in [(-1, 10, False), (100, -1, False), (100, 101, False),
                     (100.0, 10, False), (100, 10.0, False), (True, 10, False),
                     (100, True, False), (100, 10, 1), (100, 10, "yes"),
                     ("100", 10, False), (-1, 90, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli('{"paid": 10000, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})

    def test_cli_error(self):
        r = self.run_cli('{"paid": -5, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
