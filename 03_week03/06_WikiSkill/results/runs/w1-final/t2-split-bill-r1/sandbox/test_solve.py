import json
import subprocess
import sys
import unittest

from solve import split_bill


def run(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(0, 2, 50), [0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_half_up(self):
        self.assertEqual(split_bill(10, 1, 5), [11])    # 10.5 -> 11
        self.assertEqual(split_bill(11, 1, 5), [12])    # 11.55 -> 12
        self.assertEqual(split_bill(1, 1, 49), [1])     # 1.49 -> 1
        self.assertEqual(split_bill(1, 1, 50), [2])     # 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 10), [1])     # 1.1 -> 1

    def test_sum(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), (9999 * 113 * 2 + 100) // 200)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1), (10, 1, 101),
                  (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), ('10', 1, 0),
                  (None, 1, 0), (True, 1, 0), (10, True, 0), (10, 1, False)]:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)

    def test_cli_ok(self):
        code, out = run(json.dumps({'total': 1000, 'people': 3, 'tip_percent': 0}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': [334, 333, 333]})

    def test_cli_error(self):
        for payload in [json.dumps({'total': 1000, 'people': 0, 'tip_percent': 0}),
                        json.dumps({'total': 1000}), 'not json',
                        json.dumps({'total': 10.5, 'people': 1, 'tip_percent': 0})]:
            code, out = run(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)['ok'])


if __name__ == '__main__':
    unittest.main()
