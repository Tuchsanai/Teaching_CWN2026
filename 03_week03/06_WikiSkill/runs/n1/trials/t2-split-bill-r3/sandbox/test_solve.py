import json
import subprocess
import sys
import unittest

from solve import split_bill


def cli(s):
    return subprocess.run([sys.executable, "solve.py"], input=s,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1*150/100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 1*110/100 = 1.1 -> 1
        self.assertEqual(split_bill(1, 1, 10), [1])

    def test_zero_and_edges(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_errors(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1),
                  (10, 1, 101), (10.0, 1, 0), (10, 1.0, 0), (10, 1, 0.0),
                  (True, 1, 0), (10, True, 0), (10, 1, True),
                  ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)

    def test_cli_ok(self):
        r = cli('{"total": 1000, "people": 3, "tip_percent": 0}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout),
                         {"ok": True, "result": [334, 333, 333]})

    def test_cli_error(self):
        for s in ['{"total": 1000.0, "people": 3, "tip_percent": 0}',
                  '{"total": 1000, "people": 0, "tip_percent": 0}',
                  '{"total": 1000}', 'not json', '[1]']:
            r = cli(s)
            self.assertEqual(r.returncode, 2, s)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
