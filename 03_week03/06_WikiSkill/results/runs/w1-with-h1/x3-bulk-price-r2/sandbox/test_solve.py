import json
import subprocess
import sys
import unittest
from fractions import Fraction

from solve import bulk_price


def expect(p, q, c):
    d = Fraction(925, 1000) if q >= 50 else Fraction(965, 1000) if q >= 10 else 1
    x = p * q * d * (Fraction(975, 1000) if c else 1) * Fraction(107, 100)
    return int(x + Fraction(1, 2)) if x >= 0 else None


def run(payload):
    r = subprocess.run([sys.executable, "solve.py"], input=payload,
                       capture_output=True, text=True)
    return r.returncode, r.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_thresholds(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> half up
        self.assertEqual(bulk_price(1000, 49, False), expect(1000, 49, False))
        self.assertEqual(bulk_price(1000, 50, False), expect(1000, 50, False))
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_half_up(self):
        # 10 * 1 *0.965*1.07 = 10.3255 -> 10 ; find a .5 case: 50 bags at 1 satang
        self.assertEqual(bulk_price(1, 1, False), 1)  # 1.07
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5 -> 54

    def test_coupon_single_rounding(self):
        for p, q, c in [(1234, 10, True), (999, 50, True), (1, 1000, True), (777, 37, True)]:
            self.assertEqual(bulk_price(p, q, c), expect(p, q, c))

    def test_invalid(self):
        bad = [(1000.0, 1, False), (True, 1, False), ("1", 1, False), (None, 1, False), (-1, 1, False),
               (1000, 0, False), (1000, 1001, False), (1000, 1.0, False), (1000, True, False),
               (1000, "1", False), (1000, None, False), (1000, 1, 1), (1000, 1, None), (1000, 1, "True")]
        for a in bad:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def test_cli(self):
        code, out = run(json.dumps({"unit_price": 1000, "qty": 1, "coupon": False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 1070})
        code, out = run(json.dumps({"unit_price": 1.5, "qty": 1, "coupon": False}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertEqual(run("not json")[0], 2)


if __name__ == "__main__":
    unittest.main()
