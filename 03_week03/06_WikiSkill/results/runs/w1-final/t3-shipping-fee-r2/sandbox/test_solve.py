import json
import subprocess
import sys
import unittest

from solve import shipping_fee as f


def cli(obj):
    p = subprocess.run([sys.executable, 'solve.py'], input=json.dumps(obj),
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)

    def test_boundaries(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 100, False), 8002)  # 8001.5 -> half-up
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)   # .5
        self.assertEqual(f(5001, 0, True), 12002)   # 12001.5
        self.assertEqual(f(5002, 0, False), 8003)   # exact
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8

    def test_express_chain(self):
        self.assertEqual(f(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False),
                  (1.0, 1, False), (True, 1, False), (1, 1.0, False),
                  (1, 1, 1), (1, 1, None), ("1", 1, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def test_cli(self):
        code, out = cli({'weight_g': 500, 'distance_km': 10, 'express': False})
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 4000})
        code, out = cli({'weight_g': 0, 'distance_km': 10, 'express': False})
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)['ok'])
        code, out = cli({'weight_g': 5})
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
