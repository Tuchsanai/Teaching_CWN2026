import json, subprocess, sys, unittest
from solve import refund


def cli(obj):
    p = subprocess.run([sys.executable, 'solve.py'], input=json.dumps(obj),
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(1000, 50, False), 500)
        self.assertEqual(refund(1000, 0, False), 1000)
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

    def test_reject(self):
        for args in [(-1, 0, False), (10, -1, False), (10, 101, False),
                     (10.0, 0, False), (10, 0.0, False), (True, 0, False),
                     (10, 0, 1), ('10', 0, False), (None, 0, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_cli(self):
        self.assertEqual(cli({'paid': 1000, 'used_percent': 50, 'restock': True}),
                         (0, {'ok': True, 'result': 438}))
        code, out = cli({'paid': -5, 'used_percent': 50, 'restock': True})
        self.assertEqual(code, 2)
        self.assertFalse(out['ok'])
        code, out = cli({'paid': 5})
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
