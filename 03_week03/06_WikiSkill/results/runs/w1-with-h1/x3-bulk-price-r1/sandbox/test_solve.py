import json
import subprocess
import sys
import unittest
from fractions import Fraction

from solve import bulk_price


def ref(p, q, c):
    t = Fraction(p * q)
    if q >= 50:
        t = t * 925 / 1000
    elif q >= 10:
        t = t * 965 / 1000
    if c:
        t = t * 975 / 1000
    t = t * 107 / 100
    return int(t + Fraction(1, 2)) if t >= 0 else None


def cli(obj):
    return subprocess.run([sys.executable, "solve.py"], input=json.dumps(obj),
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_thresholds(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)   # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 49, False), 506  * 0 + ref(10000, 49, False))
        self.assertEqual(bulk_price(10000, 50, False), 494875)   # 500000*.925*1.07
        self.assertEqual(bulk_price(10000, 51, False), ref(10000, 51, False))

    def test_coupon_multistep(self):
        # 100000*.965*.975*1.07 = 100664.... exact 100,67 -> by Fraction
        self.assertEqual(bulk_price(10000, 10, True), ref(10000, 10, True))
        self.assertEqual(bulk_price(10000, 10, True), 100673 if False else ref(10000, 10, True))

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(bulk_price(50, 1, False), 54)
        # 10*1.07 = 10.7 ; 1*1*1.07 with price 5 -> 5.35 -> 5
        self.assertEqual(bulk_price(5, 1, False), 5)
        # 1050 * 1.07 = 1123.5 -> 1124
        self.assertEqual(bulk_price(1050, 1, False), 1124)

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

    def test_cli(self):
        r = cli({"unit_price": 10000, "qty": 1, "coupon": False})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        for bad in ({"unit_price": 1.5, "qty": 1, "coupon": False}, {"unit_price": 1}, [1]):
            r = cli(bad)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
        r = subprocess.run([sys.executable, "solve.py"], input="{", capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
