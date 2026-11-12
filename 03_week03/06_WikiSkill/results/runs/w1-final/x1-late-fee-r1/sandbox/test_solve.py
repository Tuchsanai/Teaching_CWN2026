import json
import subprocess
import sys
import unittest

from solve import late_fee


def cli(obj):
    p = subprocess.run([sys.executable, 'solve.py'], input=json.dumps(obj),
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class T(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_basic(self):
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_half_up(self):

        self.assertEqual(late_fee(1000, 5), 38)   # 37.5 -> 38
        self.assertEqual(late_fee(1000, 4), 30)
        self.assertEqual(late_fee(1400, 5), 53)   # 52.5 -> 53
        self.assertEqual(late_fee(1300, 5), 49)   # 48.75
        self.assertEqual(late_fee(1100, 5), 41)   # 41.25

    def test_zero(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_errors(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     (True, 5), (100, True), ('1', 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        self.assertEqual(cli({'amount': 100000, 'days_late': 4}),
                         (0, {'ok': True, 'result': 3000}))
        code, out = cli({'amount': -1, 'days_late': 4})
        self.assertEqual(code, 2)
        self.assertFalse(out['ok'])
        code, out = cli({'amount': 5})
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
