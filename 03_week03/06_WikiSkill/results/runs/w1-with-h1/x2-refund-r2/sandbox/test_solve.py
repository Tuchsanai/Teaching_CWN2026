import json
import subprocess
import sys
import unittest

from solve import refund


class RefundTest(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)

    def test_threshold(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 79, False), 210)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_restock(self):
        # 10000*0.5*0.875 = 4375
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_half_up(self):
        # 1*0.5 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 4*0.5*0.875 = 1.75 -> 2 ; 2*0.75*0.875=1.3125 -> 1
        self.assertEqual(refund(4, 50, True), 2)
        self.assertEqual(refund(2, 25, True), 1)
        # 12*0.5*0.875 = 5.25 ; 4*0.5=2 ; 1*0.875*1=0.875->1
        self.assertEqual(refund(1, 0, True), 1)
        # 4 * 0.875 = 3.5 -> 4 (single rounding)
        self.assertEqual(refund(4, 0, True), 4)

    def test_invalid(self):
        bad = [
            (4500.0, 10, False), (True, 10, False), ("1", 10, False),
            (None, 10, False), (-1, 10, False),
            (100, 10.0, False), (100, True, False), (100, "1", False),
            (100, None, False), (100, -1, False), (100, 101, False),
            (100, 10, 1), (100, 10, None), (100, 10, "True"),
        ]
        for args in bad:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"paid": 10000, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        r = self.run_cli('{"paid": 1.5, "used_percent": 50, "restock": true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(self.run_cli("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
