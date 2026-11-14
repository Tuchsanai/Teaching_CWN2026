import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    def test_proportional(self):
        self.assertEqual(refund(10000, 25, False), 7500)

    def test_over_80_zero(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_exactly_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_restock_fee(self):
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_round_half_up_once(self):
        # 1 * 50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 1 * 0.875 = 0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)
        # 4*0.9*0.875 = 3.15 -> 3 ; 2*(100-50)/100*.875=0.875
        self.assertEqual(refund(4, 10, True), 3)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    def test_invalid(self):
        for args in [(-1, 0, True), (1.0, 0, True), (True, 0, True),
                     (1, 101, True), (1, -1, True), (1, 0, 1), (1, "5", False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(
            {"paid": 10000, "used_percent": 0, "restock": True}),
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 8750})
        p = subprocess.run([sys.executable, "solve.py"], input="{}",
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
