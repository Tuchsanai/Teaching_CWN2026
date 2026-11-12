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

    def test_half_up(self):
        # 10010*0.015=150.15 -> 150 ; 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10100, 'silver', False), 152)
        self.assertEqual(cashback(10040, 'silver', False), 151)  # 150.6
        self.assertEqual(cashback(10010, 'silver', False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, 'platinum', False), 20000)
        self.assertEqual(cashback(500000, 'platinum', True), 20000)
        self.assertEqual(cashback(500000, 'gold', False), 12500)

    def test_invalid(self):
        for args in [(-1, 'gold', False), (100.0, 'gold', False),
                     (True, 'gold', False), ('1', 'gold', False),
                     (None, 'gold', False), (10000, 'bronze', False),
                     (10000, None, False), (10000, 'gold', 1),
                     (10000, 'gold', None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli_ok(self):
        code, out = cli('{"amount": 20000, "tier": "gold", "birthday": true}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 1000})

    def test_cli_error(self):
        for s in ['{"amount": 1.5, "tier": "gold", "birthday": true}',
                  '{"amount": 100}', 'not json']:
            code, out = cli(s)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)['ok'])


if __name__ == '__main__':
    unittest.main()
