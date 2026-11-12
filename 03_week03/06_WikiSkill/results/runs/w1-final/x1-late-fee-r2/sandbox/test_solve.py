import json
import subprocess
import sys
import unittest

from solve import late_fee


def run(payload):
    return subprocess.run([sys.executable, 'solve.py'], input=payload,
                          capture_output=True, text=True)


class TestLateFee(unittest.TestCase):
    def test_no_fee_up_to_3(self):
        for d in (0, 1, 3):
            self.assertEqual(late_fee(100000, d), 0)

    def test_basic(self):
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        # 200*4*0.0075 = 6.0 ; 10*4*.0075=0.3 ; 70*4*.0075=2.1
        self.assertEqual(late_fee(10, 4), 0)
        # 50*... .5 exact: amount 200, 5 days -> 200*375/10000 = 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        # 0.6 -> 1 : amount 20, 4 days -> 0.6
        self.assertEqual(late_fee(20, 4), 1)
        # 0.4 -> 0 : amount 13, 4 days -> 0.39
        self.assertEqual(late_fee(13, 4), 0)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_invalid(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ('1', 5), (100, None), (True, 5), (100, True)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli_ok(self):
        r = run(json.dumps({'amount': 100000, 'days_late': 4}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 3000})

    def test_cli_error(self):
        for p in (json.dumps({'amount': -5, 'days_late': 4}),
                  json.dumps({'amount': 5}), 'not json'):
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)['ok'])
            self.assertNotIn('Traceback', r.stderr)


if __name__ == '__main__':
    unittest.main()
