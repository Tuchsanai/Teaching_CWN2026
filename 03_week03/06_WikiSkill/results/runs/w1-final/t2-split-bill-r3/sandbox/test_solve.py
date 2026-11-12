import json
import subprocess
import sys
import unittest

from solve import split_bill


def run(payload):
    return subprocess.run([sys.executable, 'solve.py'], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])
        self.assertEqual(split_bill(1000, 1, 100), [2000])

    def test_half_up(self):
        self.assertEqual(split_bill(5, 1, 10), [6])    # 5.5 -> 6
        self.assertEqual(split_bill(14, 1, 10), [15])  # 15.4 -> 15
        self.assertEqual(split_bill(1, 1, 50), [2])    # 1.5 -> 2
        self.assertEqual(split_bill(6, 1, 10), [7])    # 6.6 -> 7

    def test_invalid(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                     (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                     (True, 1, 0), (10, True, 0), ('10', 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        r = run(json.dumps({'total': 1000, 'people': 3, 'tip_percent': 0}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': [334, 333, 333]})
        for p in [json.dumps({'total': 10, 'people': 0, 'tip_percent': 0}),
                  json.dumps({'total': 10}), 'garbage']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
