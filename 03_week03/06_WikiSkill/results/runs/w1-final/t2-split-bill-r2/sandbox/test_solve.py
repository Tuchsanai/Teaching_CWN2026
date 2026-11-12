import json
import subprocess
import sys
import unittest

from solve import split_bill


def cli(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_half_up(self):
        self.assertEqual(sum(split_bill(5, 1, 10)), 6)    # 5.5 -> 6
        self.assertEqual(sum(split_bill(1, 1, 50)), 2)    # 1.5 -> 2
        self.assertEqual(sum(split_bill(106, 1, 5)), 111)  # 111.3 -> 111
        self.assertEqual(sum(split_bill(11, 1, 5)), 12)   # 11.55 -> 12

    def test_boundary(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(sum(split_bill(999, 7, 13)), 1129)

    def test_reject(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), (True, 1, 0),
                     ('1', 1, 0), (None, 1, 0), (1, 1, True)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli_ok(self):
        code, out = cli(json.dumps({'total': 100, 'people': 3, 'tip_percent': 0}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': [34, 33, 33]})

    def test_cli_error(self):
        for payload in [json.dumps({'total': 100, 'people': 0, 'tip_percent': 0}),
                        json.dumps({'total': 100}), 'not json']:
            code, out = cli(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)['ok'])


if __name__ == '__main__':
    unittest.main()
