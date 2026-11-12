import json
import subprocess
import sys
import unittest
from fractions import Fraction

from solve import bulk_price


def expected(p, q, c):
    x = Fraction(p * q)
    if q >= 50:
        x = x * 925 / 1000
    elif q >= 10:
        x = x * 965 / 1000
    if c:
        x = x * 975 / 1000
    x = x * 107 / 100
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 -> 10433

    def test_thresholds(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)   # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 49, False), expected(10000, 49, False))
        self.assertEqual(bulk_price(10000, 50, False), 494875)   # 500000*.925*1.07
        self.assertEqual(bulk_price(10000, 51, False), expected(10000, 51, False))

    def test_half_up(self):
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54

    def test_multi_step(self):
        self.assertEqual(bulk_price(333, 50, True), expected(333, 50, True))
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_invalid(self):
        bad = [
            (4500.0, 1, False), (True, 1, False), ("1", 1, False), (None, 1, False), (-1, 1, False),
            (100, 1.0, False), (100, True, False), (100, "1", False), (100, None, False),
            (100, 0, False), (100, 1001, False),
            (100, 1, 1), (100, 1, 0), (100, 1, None), (100, 1, "True"),
        ]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                bulk_price(*a)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s, capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli(json.dumps({"unit_price": 10000, "qty": 10, "coupon": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 103255})
        for s in ['{"unit_price": 1.5, "qty": 1, "coupon": false}', 'bad', '[]', '{"qty": 1}']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
