import json
import subprocess
import sys
import unittest

from solve import late_fee


def run(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(0, 10), 0)

    def test_grace_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        self.assertEqual(late_fee(200, 10), 15)    # 15.0
        self.assertEqual(late_fee(10, 10), 1)      # 0.75 -> 1
        self.assertEqual(late_fee(2, 10), 0)       # 0.15 -> 0
        self.assertEqual(late_fee(20, 10), 2)      # 1.5 -> 2
        self.assertEqual(late_fee(1000, 5), 38)    # 37.5 -> 38
        self.assertEqual(late_fee(1020, 5), 38)    # 38.25 -> 38
        self.assertEqual(late_fee(1040, 5), 39)    # 39.0

    def test_errors(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     (True, 5), (100, True), ('100', 5), (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli_ok(self):
        code, out = run(json.dumps({'amount': 100000, 'days_late': 10}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 7500})

    def test_cli_error(self):
        for payload in [json.dumps({'amount': -1, 'days_late': 5}),
                        json.dumps({'amount': 5}), 'not json']:
            code, out = run(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)['ok'])


if __name__ == '__main__':
    unittest.main()
