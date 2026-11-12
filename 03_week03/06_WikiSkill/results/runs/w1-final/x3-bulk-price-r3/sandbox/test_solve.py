import json
import subprocess
import sys
import unittest

from solve import bulk_price


def run(payload):
    return subprocess.run([sys.executable, 'solve.py'], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundaries(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)   # 96.5%
        self.assertEqual(bulk_price(10000, 49, False), 505950)   # 505949.5 half-up
        self.assertEqual(bulk_price(10000, 50, False), 494875)   # 92.5% only

    def test_coupon(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 -> half-up

    def test_half_up(self):
        # 100*1*1.07 = 107 ; 5*1.07=5.35 -> 5 ; 10*1.07*... use .5 case
        self.assertEqual(bulk_price(50, 1, True), 52)   # 52.156
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # exactly .5
        self.assertEqual(bulk_price(1, 10, False), 10)  # 10.3255 -> 10
        self.assertEqual(bulk_price(1, 1, False), 1)    # 1.07

    def test_invalid(self):
        for args in [(-1, 1, False), (1, 0, False), (1, 1001, False),
                     (1.0, 1, False), (1, 1.0, False), (True, 1, False),
                     (1, True, False), ('1', 1, False), (None, 1, False),
                     (1, 1, 1), (1, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli_ok(self):
        r = run(json.dumps({'unit_price': 10000, 'qty': 1, 'coupon': False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 10700})

    def test_cli_error(self):
        for p in [json.dumps({'unit_price': 1, 'qty': 0, 'coupon': False}),
                  json.dumps({'unit_price': 1}), 'not json']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
