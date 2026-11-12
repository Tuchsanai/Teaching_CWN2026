import json
import subprocess
import sys
import unittest

from solve import cashback


def cli(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, 'silver', False), 300)
        self.assertEqual(cashback(20000, 'gold', False), 500)
        self.assertEqual(cashback(20000, 'platinum', False), 800)
        self.assertEqual(cashback(20000, 'gold', True), 1000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, 'platinum', True), 0)
        self.assertEqual(cashback(10000, 'platinum', False), 400)
        self.assertEqual(cashback(0, 'gold', False), 0)

    def test_cap_boundary(self):
        self.assertEqual(cashback(500000, 'platinum', False), 20000)
        self.assertEqual(cashback(500001, 'platinum', False), 20000)
        self.assertEqual(cashback(499980, 'platinum', False), 19999)
        self.assertEqual(cashback(1000000, 'platinum', True), 20000)

    def test_half_up(self):
        # 10100*0.015 = 151.5 -> 152 ; 10110*.015=151.65 -> 152
        self.assertEqual(cashback(10100, 'silver', False), 152)
        self.assertEqual(cashback(10110, 'silver', False), 152)
        self.assertEqual(cashback(10120, 'silver', False), 152)  # 151.8
        self.assertEqual(cashback(10030, 'silver', False), 150)  # 150.45
        # birthday doubles before rounding: 10010*.015*2=300.3
        self.assertEqual(cashback(10010, 'silver', True), 300)
        # 10150*.015=152.25 ; 10010*.025=250.25 ; 10030*.025=250.75
        self.assertEqual(cashback(10030, 'gold', False), 251)
        self.assertEqual(cashback(10010, 'gold', False), 250)

    def test_value_errors(self):
        for args in [(-1, 'gold', False), (100.0, 'gold', False),
                     (True, 'gold', False), (None, 'gold', False),
                     ('100', 'gold', False), (20000, 'bronze', False),
                     (20000, None, False), (20000, 'gold', 1),
                     (20000, 'gold', None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli_ok(self):
        code, out = cli(json.dumps({'amount': 20000, 'tier': 'gold', 'birthday': True}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 1000})

    def test_cli_error(self):
        for payload in [json.dumps({'amount': -5, 'tier': 'gold', 'birthday': False}),
                        json.dumps({'amount': 1}), 'not json']:
            code, out = cli(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)['ok'])


if __name__ == '__main__':
    unittest.main()
