import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    def test_proportional(self):
        self.assertEqual(refund(1000, 50, False), 500)

    def test_restock_half_up(self):
        self.assertEqual(refund(1000, 50, True), 438)

    def test_over_80_zero(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_exactly_80(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_zero_used_restock(self):
        self.assertEqual(refund(800, 0, True), 700)

    def test_invalid(self):
        for args in [(1.0, 5, True), (True, 5, True), (-1, 5, True),
                     (100, 101, True), (100, -1, False), (100, 5, 1),
                     (100, 5.0, True), ("1", 5, True), (None, 5, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli_ok(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"paid":1000,"used_percent":50,"restock":true}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 438})

    def test_cli_bad(self):
        for s in ["not json", '{"paid":1}', '[1]']:
            p = subprocess.run([sys.executable, "solve.py"], input=s, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
