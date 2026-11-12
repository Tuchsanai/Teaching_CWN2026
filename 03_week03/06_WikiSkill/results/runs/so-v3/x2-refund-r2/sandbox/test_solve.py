import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    def test_proportional(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock_fee(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_over_80_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_exactly_80_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_zero_paid_and_unused(self):
        self.assertEqual(refund(0, 10, True), 0)
        self.assertEqual(refund(800, 0, False), 800)

    def test_half_up_rounding(self):
        # 1 * 50 * 875 over 100000 = 0.4375 -> 0 ; 4 * 50 / 100 = 2 exact
        self.assertEqual(refund(4, 50, False), 2)
        self.assertEqual(refund(1, 50, False), 1)

    def test_invalid(self):
        for args in [(-1, 0, False), (1, 101, False), (1, -1, True),
                     (1.0, 0, False), (True, 0, False), ("1", 0, False),
                     (1, 0, 1), (1, 0, None), (1, 5.0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        def run(inp):
            p = subprocess.run([sys.executable, "solve.py"], input=inp,
                               capture_output=True, text=True)
            return p.returncode, json.loads(p.stdout)
        self.assertEqual(run('{"paid": 10000, "used_percent": 50, "restock": true}'),
                         (0, {"ok": True, "result": 4375}))
        self.assertEqual(run("{bad")[0], 2)
        self.assertEqual(run('{"paid": 1}'), (2, run('{"paid": 1}')[1]))
        self.assertFalse(run('{"paid": 1}')[1]["ok"])


if __name__ == "__main__":
    unittest.main()
