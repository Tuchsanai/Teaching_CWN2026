import json
import subprocess
import sys
import unittest

from solve import cashback


def run(payload):
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
        self.assertEqual(cashback(0, 'gold', False), 0)
        self.assertEqual(cashback(10000, 'platinum', False), 400)

    def test_cap(self):
        self.assertEqual(cashback(500000, 'platinum', False), 20000)  # exactly 20000
        self.assertEqual(cashback(500001, 'platinum', False), 20000)
        self.assertEqual(cashback(10**7, 'platinum', True), 20000)
        self.assertEqual(cashback(499999, 'platinum', False), 20000)  # 19999.96 -> 20000

    def test_half_up(self):
        # silver 1.5%: 10100*0.015 = 151.5 -> 152
        self.assertEqual(cashback(10100, 'silver', False), 152)
        # 10110*0.015 = 151.65 -> 152
        self.assertEqual(cashback(10110, 'silver', False), 152)
        # 10120*0.015=151.8; 10010*0.015=150.15 -> 150
        self.assertEqual(cashback(10010, 'silver', False), 150)
        # gold 2.5%: 10010*0.025 = 250.25 ; 10030*0.025=250.75 -> 251
        self.assertEqual(cashback(10030, 'gold', False), 251)
        # birthday: 10100*0.03 = 303
        self.assertEqual(cashback(10100, 'silver', True), 303)
        # birthday not double-rounded: 10101*0.03=303.03
        self.assertEqual(cashback(10101, 'silver', True), 303)

    def test_errors(self):
        bad = [(-1, 'gold', False), (100.0, 'gold', False), ('100', 'gold', False),
               (None, 'gold', False), (True, 'gold', False),
               (10000, 'bronze', False), (10000, None, False), (10000, 1, False),
               (10000, 'gold', 1), (10000, 'gold', None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                cashback(*a)

    def test_cli_ok(self):
        code, out = run(json.dumps({'amount': 20000, 'tier': 'gold', 'birthday': False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 500})

    def test_cli_error(self):
        for payload in [json.dumps({'amount': -5, 'tier': 'gold', 'birthday': False}),
                        json.dumps({'amount': 100}), 'not json',
                        json.dumps({'amount': 1.5, 'tier': 'gold', 'birthday': False})]:
            code, out = run(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)['ok'])


if __name__ == '__main__':
    unittest.main()
