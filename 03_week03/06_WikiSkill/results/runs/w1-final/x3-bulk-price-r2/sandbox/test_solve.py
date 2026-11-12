import json
import subprocess
import sys
import unittest
from fractions import Fraction

from solve import bulk_price


def ref(u, q, c):
    v = Fraction(u * q)
    if q >= 50:
        v *= Fraction(925, 1000)
    elif q >= 10:
        v *= Fraction(965, 1000)
    if c:
        v *= Fraction(975, 1000)
    v *= Fraction(107, 100)
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))


def run(payload):
    return subprocess.run([sys.executable, 'solve.py'], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundaries(self):
        for q in (1, 9, 10, 11, 49, 50, 51, 1000):
            for c in (False, True):
                self.assertEqual(bulk_price(12345, q, c), ref(12345, q, c))
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255 if False else ref(10000, 10, False))
        self.assertLess(bulk_price(10000, 50, False), bulk_price(10000, 49, False))

    def test_half_up(self):
        # 1*1*1.07 = 1.07 -> 1 ; 50 -> 1 bag *? use search for exact .5 / .6
        self.assertEqual(bulk_price(1, 1, False), 1)
        self.assertEqual(bulk_price(50, 1, False), 54)   # 53.5 -> 54
        self.assertEqual(bulk_price(10, 1, False), 11)   # 10.7
        self.assertEqual(bulk_price(5, 1, False), 5)     # 5.35

    def test_random_vs_ref(self):
        import random
        r = random.Random(1)
        for _ in range(2000):
            u, q, c = r.randint(0, 100000), r.randint(1, 1000), r.random() < .5
            self.assertEqual(bulk_price(u, q, c), ref(u, q, c))

    def test_invalid(self):
        bad = [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
               (1, 1.0, False), (True, 1, False), (1, True, False),
               (1, 1, 1), (1, 1, None), ('1', 1, False), (None, 1, False)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                bulk_price(*a)

    def test_cli_ok(self):
        p = run(json.dumps({'unit_price': 10000, 'qty': 1, 'coupon': False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {'ok': True, 'result': 10700})

    def test_cli_error(self):
        for s in ('{"unit_price": -1, "qty": 1, "coupon": false}',
                  '{"unit_price": 1}', 'not json',
                  '{"unit_price": 1.5, "qty": 1, "coupon": false}'):
            p = run(s)
            self.assertEqual(p.returncode, 2, s)
            self.assertFalse(json.loads(p.stdout)['ok'])
            self.assertNotIn('Traceback', p.stderr)


if __name__ == '__main__':
    unittest.main()
