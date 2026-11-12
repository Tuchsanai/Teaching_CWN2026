import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    def test_full_refund_no_restock(self):
        self.assertEqual(refund(1000, 0, False), 1000)

    def test_proportional(self):
        self.assertEqual(refund(1000, 50, False), 500)

    def test_restock_fee(self):
        self.assertEqual(refund(800, 0, True), 700)

    def test_over_80_zero(self):
        self.assertEqual(refund(1000, 81, False), 0)

    def test_exactly_80_refunds(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_half_up_single_rounding(self):
        self.assertEqual(refund(4, 50, True), 2)

    def test_invalid_inputs(self):
        for args in [(5.0, 0, False), (True, 0, False), (-1, 0, False),
                     (10, 101, False), (10, -1, False), (10, 5, 1),
                     (None, 5, True), (10, "5", True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input=json.dumps(
                               {"paid": 800, "used_percent": 0, "restock": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 700})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input="{bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
