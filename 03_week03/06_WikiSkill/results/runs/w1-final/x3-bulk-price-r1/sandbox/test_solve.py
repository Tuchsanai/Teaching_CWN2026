import json
import subprocess
import sys
import unittest

from solve import bulk_price


def run(obj):
    p = subprocess.run([sys.executable, 'solve.py'], input=json.dumps(obj),
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 -> half-up

    def test_boundaries(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_half_up(self):
        self.assertEqual(bulk_price(50, 1, False), 54)   # 53.5
        self.assertEqual(bulk_price(10, 1, False), 11)   # 10.7
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_value_errors(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                     (100.0, 1, False), (100, 1.0, False), (True, 1, False),
                     (100, 1, 1), (100, 1, None), ('1', 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli(self):
        self.assertEqual(run({'unit_price': 10000, 'qty': 50, 'coupon': False}),
                         (0, {'ok': True, 'result': 494875}))
        code, out = run({'unit_price': 100, 'qty': 0, 'coupon': False})
        self.assertEqual(code, 2)
        self.assertFalse(out['ok'])
        code, out = run({'unit_price': 100})
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
