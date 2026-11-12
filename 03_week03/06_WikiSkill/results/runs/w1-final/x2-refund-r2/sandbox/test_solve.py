import json
import subprocess
import sys
import unittest

from solve import refund


def run(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(1000, 0, False), 1000)
        self.assertEqual(refund(1000, 50, False), 500)
        self.assertEqual(refund(1000, 50, True), 438)  # 437.5 -> half-up
        self.assertEqual(refund(0, 10, True), 0)

    def test_boundary(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_half_up(self):
        self.assertEqual(refund(1, 50, False), 1)   # 0.5 -> 1
        self.assertEqual(refund(3, 50, False), 2)   # 1.5 -> 2
        self.assertEqual(refund(1, 40, False), 1)   # 0.6 -> 1
        self.assertEqual(refund(1, 60, False), 0)   # 0.4 -> 0

    def test_invalid(self):
        for args in [(-1, 0, False), (10, -1, False), (10, 101, False),
                     (10.0, 0, False), (10, 0.0, False), (True, 0, False),
                     (10, 0, 1), ('10', 0, False), (None, 0, False),
                     (10, True, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        code, out = run(json.dumps({'paid': 1000, 'used_percent': 50, 'restock': True}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 438})
        code, out = run(json.dumps({'paid': 1000, 'used_percent': 500, 'restock': True}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)['ok'])
        code, out = run('{"paid": 1}')
        self.assertEqual(code, 2)
        code, out = run('not json')
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
